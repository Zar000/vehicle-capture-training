import cv2
import os
from datetime import datetime
import time
import re

RTSP_URL = "[rtsp://[Your Camera username]:[Your camera user password]@[Your Camera IP]/stream1]"
SAVE_EVERY_SECONDS = 5
DAY_START_HOUR = 8
DAY_END_HOUR = 17

def is_daytime():
    now = datetime.now().hour
    return DAY_START_HOUR <= now <= DAY_END_HOUR

def make_output_folder():
    folder_name = datetime.now().strftime("dataset_%Y-%m-%d")
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def get_start_index(folder):
    files = os.listdir(folder)
    numbers = []

    pattern = re.compile(r"img_(\d+)\.jpg")

    for f in files:
        match = pattern.match(f)
        if match:
            numbers.append(int(match.group(1)))

    if not numbers:
        return 0

    return max(numbers) + 1

def open_stream():
    """Open RTSP stream with FFmpeg backend."""
    print("[INFO] Opening RTSP stream...")
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    time.sleep(1)
    return cap

def main():
    output_folder = make_output_folder()
    img_count = get_start_index(output_folder)

    cap = open_stream()

    if not cap.isOpened():
        print("[ERROR] Could not connect to camera")
        return

    while True:
        if not is_daytime():
            print("[INFO] Nighttime detected — waiting...")
            time.sleep(60)
            continue

        ret, frame = cap.read()

        if not ret:
            print("\n[WARN] Lost RTSP connection, reconnecting...")
            cap.release()
            time.sleep(2)
            cap = open_stream()
            continue

        filename = os.path.join(output_folder, f"img_{img_count:05d}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved {filename}", end="\r")

        img_count += 1
        time.sleep(SAVE_EVERY_SECONDS)

    cap.release()

if __name__ == "__main__":
    main()
