import cv2
import numpy as np
import os
import json
import time
import base64
import requests
from datetime import datetime
from ultralytics import YOLO
from zebra_detector import detect_zebra
import serial

YOLO_MODEL_PATH = r"C:\Users\Naila\PycharmProjects\PythonProject\PythonProject\Iotnewsession\runs\detect\train2\weights\best.pt"
SERVER_URL = "http://13.48.46.60/upload_event.php"

IR_COM_PORT = "COM3"
IR_BAUDRATE = 9600

CAMERA_INDEX = 2                 # 🔒 LOCKED external USB webcam
IDLE_SHUTDOWN_SEC = 20           # camera off after no IR motion
EVENT_COOLDOWN_SEC = 5           # prevent event spamming

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# ======================================================
# LOAD YOLO MODEL
# ======================================================
model = YOLO(YOLO_MODEL_PATH)

# ======================================================
# IR SENSOR (SAFE INITIALIZATION)
# ======================================================
try:
    ser = serial.Serial(IR_COM_PORT, IR_BAUDRATE, timeout=1)
    time.sleep(2)
    print("✅ IR sensor connected")
except Exception as e:
    print("⚠ IR sensor not available — camera will stay ON")
    ser = None

def ir_motion_detected():
    if ser is None:
        return True
    if ser.in_waiting:
        line = ser.readline().decode(errors="ignore").strip()
        if line == "MOTION":
            return True
    return False

# ======================================================
# EVENT CREATION
# ======================================================
def create_event(event_type, frame, zebra_found, person_count):
    os.makedirs("events", exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"events/{event_type}_{timestamp}.jpg"
    cv2.imwrite(filename, frame)

    event = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "location": "Camera_02",
        "zebra_found": zebra_found,
        "person_count": person_count,
        "image_path": filename
    }

    print("\nEVENT GENERATED:")
    print(json.dumps(event, indent=4))
    return event

# ======================================================
# SEND EVENT TO SERVER
# ======================================================
def send_event_to_server(event):
    with open(event["image_path"], "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    payload = {
        "event_type": event["event_type"],
        "timestamp": event["timestamp"],
        "location": event["location"],
        "zebra_found": event["zebra_found"],
        "person_count": event["person_count"],
        "image_base64": img_b64
    }

    try:
        r = requests.post(SERVER_URL, json=payload, timeout=5)
        print("Server:", r.text)
    except Exception as e:
        print("❌ Server error:", e)

# ======================================================
# CAMERA CONTROL (LOCKED INDEX)
# ======================================================
cap = None
camera_running = False

def start_camera():
    global cap, camera_running
    if camera_running:
        return

    print(f"📷 Opening webcam at index {CAMERA_INDEX}...")
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("❌ Failed to open webcam at index", CAMERA_INDEX)
        cap.release()
        cap = None
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    camera_running = True
    print("✅ Camera STARTED (external USB webcam)")

def stop_camera():
    global cap, camera_running
    if camera_running:
        cap.release()
        cap = None
        camera_running = False
        print("🛑 Camera STOPPED")

# ======================================================
# MOTION BACKGROUND MODEL
# ======================================================
bg = cv2.createBackgroundSubtractorMOG2(
    history=300,
    varThreshold=40,
    detectShadows=False
)

# ======================================================
# MAIN LOOP
# ======================================================
print("🚦 System started. Waiting for IR motion...")

last_motion_time = 0
last_event_time = 0

while True:

    # ---------------- IR CONTROL ----------------
    if ir_motion_detected():
        last_motion_time = time.time()
        if not camera_running:
            start_camera()
    else:
        if camera_running and (time.time() - last_motion_time > IDLE_SHUTDOWN_SEC):
            stop_camera()

    if not camera_running:
        time.sleep(0.2)
        continue

    # ---------------- CAMERA FRAME ----------------
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    # ---------------- ZEBRA DETECTION ----------------
    zebra_found, stripes, zebra_top, zebra_bottom = detect_zebra(frame)

    if not zebra_found:
        cv2.putText(frame, "NO ZEBRA", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imshow("Detector", frame)
        cv2.waitKey(1)
        continue

    # ---------------- MOTION MASK ----------------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    motion_mask = bg.apply(gray)
    _, motion_mask = cv2.threshold(motion_mask, 40, 255, cv2.THRESH_BINARY)
    motion_mask = cv2.dilate(motion_mask, None, iterations=2)
    motion_count = np.sum(motion_mask) // 255

    # ---------------- YOLO DETECTION ----------------
    if motion_count > 1500:
        results = model(frame, verbose=False)
        person_count = 0

        for result in results:
            for box in result.boxes:
                if int(box.cls[0]) != 0:
                    continue

                person_count += 1
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                center_y = (y1 + y2) // 2

                if zebra_top <= center_y <= zebra_bottom:
                    event_type = "safe_crossing"
                    label = "SAFE"
                    color = (0, 255, 0)
                else:
                    event_type = "jaywalking"
                    label = "JAYWALKING"
                    color = (0, 0, 255)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                # -------- EVENT COOLDOWN --------
                if time.time() - last_event_time < EVENT_COOLDOWN_SEC:
                    continue

                last_event_time = time.time()
                event = create_event(event_type, frame, True, person_count)
                send_event_to_server(event)

    cv2.imshow("Detector", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ======================================================
# CLEANUP
# ======================================================
stop_camera()
cv2.destroyAllWindows()
if ser:
    ser.close()
