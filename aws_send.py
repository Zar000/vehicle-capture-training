import cv2
import os
import time
from datetime import datetime
import re
from collections import Counter
import json
from threading import Event

from ultralytics import YOLO
from awscrt import mqtt
from awsiot import mqtt_connection_builder

# ---------------- CONFIG ----------------
RTSP_URL = "[rtsp://[Your Camera username]:[Your camera user password]@[Your Camera IP]/stream1]"
# Change this path to your own trained model best path.
MODEL_PATH = "/home/zaro/models/best.pt"
# Change accordingly
THING_NAME = "rpi4-cam"
# Make sure to get your own endpoint
IOT_ENDPOINT = "changeMe-ats.iot.eu-central-1.amazonaws.com"

# make sure to have your certificates on the raspberry pi or other MCU that will be sending data.
CERT = "/home/zaro/certs/rpi4-certificate.pem.crt"
KEY = "/home/zaro/certs/rpi4-private.pem.key"
CA = "/home/zaro/certs/AmazonRootCA1.pem"

# Change to your own relevant topic
DETECTION_TOPIC = "camera/detections"

# Default settings (shadow can override)
SAVE_EVERY_SECONDS = 60
DAY_START_HOUR = 8
DAY_END_HOUR = 17

# Global MQTT connection object
mqtt_conn = None
connected_event = Event()
# ----------------------------------------

def open_stream():
    print("[INFO] Opening RTSP stream...")
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    time.sleep(1)
    return cap


def detect_objects(model, frame):
    results = model.predict(frame, verbose=False)
    detection_counts = Counter()

    for r in results:
        for cls_idx in r.boxes.cls.cpu().numpy():
            detection_counts[int(cls_idx)] += 1

    names = model.names
    detection_json = {names[k]: int(v) for k, v in detection_counts.items()}
    return detection_json


# ---------------- MQTT HANDLERS ----------------

def on_connection_interrupted(connection, error, **kwargs):
    print(f"[ERROR] Connection interrupted: {error}")


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(f"[INFO] Connection resumed: {return_code} (session_present={session_present})")


# ---------------- SHADOW HANDLING ----------------

def shadow_delta_callback(topic, payload, dup, qos, retain, **kwargs):
    """
    Handles shadow update/delta (remote desired state changes)
    """
    global SAVE_EVERY_SECONDS

    data = json.loads(payload)
    print("\n[SHADOW DELTA RECEIVED]", data)

    if "state" in data:
        delta = data["state"]

        # Remote update interval
        if "detection_interval" in delta:
            SAVE_EVERY_SECONDS = delta["detection_interval"]
            print(f"[INFO] Updated detection interval via shadow: {SAVE_EVERY_SECONDS}")

    # Clear delta by updating reported AND clearing desired
    update_shadow({
        "detection_interval": SAVE_EVERY_SECONDS
    })


def update_shadow(reported_state: dict):
    """
    Reports state to AWS IoT Shadow and clears desired state.
    """
    shadow_payload = {
        "state": {
            "reported": reported_state,
            "desired": None
        }
    }

    mqtt_conn.publish(
        topic=f"$aws/things/{THING_NAME}/shadow/update",
        payload=json.dumps(shadow_payload),
        qos=mqtt.QoS.AT_LEAST_ONCE
    )
    print("[SHADOW] Updated:", reported_state)


# ---------------- MAIN ----------------

def main():
    global mqtt_conn

    # Connect to IoT
    mqtt_conn = mqtt_connection_builder.mtls_from_path(
        endpoint=IOT_ENDPOINT,
        cert_filepath=CERT,
        pri_key_filepath=KEY,
        ca_filepath=CA,
        client_id=THING_NAME,
        clean_session=False,
        keep_alive_secs=30,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed
    )

    print("[INFO] Connecting to AWS IoT Core...")
    connect_future = mqtt_conn.connect()
    connect_future.result()
    print("[INFO] Connected to AWS IoT MQTT!")

    # Subscribe to shadow delta messages
    mqtt_conn.subscribe(
        topic=f"$aws/things/{THING_NAME}/shadow/update/delta",
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=shadow_delta_callback
    )

    # Load YOLO model
    model = YOLO(MODEL_PATH)

    # Open camera
    cap = open_stream()
    if not cap.isOpened():
        print("[ERROR] Cannot connect to RTSP camera.")
        return

    # MAIN LOOP
    while True:

        ret, frame = cap.read()
        if not ret:
            print("[WARN] RTSP connection lost — reconnecting...")
            cap.release()
            time.sleep(2)
            cap = open_stream()
            continue

        # YOLO detection
        detections = detect_objects(model, frame)

        message = {
            "device": THING_NAME,
            "timestamp": int(time.time() * 1000),  # milliseconds for lambda conversion
            "sedan": detections.get("sedan", 0),
            "suv": detections.get("suv", 0),
            "bus": detections.get("bus", 0),
            "van": detections.get("van", 0),
            "ambulance": detections.get("ambulance", 0),
            "police": detections.get("police", 0),
            "firetruck": detections.get("firetruck", 0),
            "motorcycle": detections.get("motorcycle", 0)
        }



        # Publish detection
        mqtt_conn.publish(
            topic=DETECTION_TOPIC,
            payload=json.dumps(message),
            qos=mqtt.QoS.AT_LEAST_ONCE
        )

        print("[DETECTED]", message)

        # Update shadow with live info
        update_shadow({
            "last_detection": detections,
            "timestamp": datetime.now().isoformat(),
            "online": True,
            "detection_interval": SAVE_EVERY_SECONDS
        })

        time.sleep(SAVE_EVERY_SECONDS)


if __name__ == "__main__":
    main()
