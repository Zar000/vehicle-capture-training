import cv2

username = "yourCamUser"
password = "yourCampassword"
#Ensure that the IP is the IP of your camera
ip = "192.168.1.210"

rtsp_url = f"rtsp://{username}:{password}@{ip}/stream1"

cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Failed to connect to the camera.")
    exit()

ret, frame = cap.read()
if ret:
    cv2.imwrite("snapshot.jpg", frame)
    print("Snapshot saved as snapshot.jpg")
    
    cv2.imshow("Snapshot", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Failed to capture frame.")

cap.release()
