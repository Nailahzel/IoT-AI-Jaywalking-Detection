import cv2
import numpy as np
from ultralytics import YOLO
import imutils

# ------------------ LOAD YOLO MODEL --------------------
model = YOLO(r"C:\Users\Naila\PycharmProjects\PythonProject\PythonProject\Iotnewsession\runs\detect\train2\weights\best.pt")


# ------------------ ZEBRA CROSSING DETECTION --------------------
def detect_zebra(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    stripes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        if w > 100 and 10 < h < 60:
            stripes.append((x, y, w, h))

    if len(stripes) >= 3:
        ys = [y for (_, y, _, _) in stripes]
        zebra_top = min(ys) - 10
        zebra_bottom = max([y + h for (_, y, _, h) in stripes]) + 10
        return True, stripes, zebra_top, zebra_bottom
    return False, [], None, None


# ------------------ MAIN DETECTION LOOP --------------------
cap = cv2.VideoCapture(0)
bg = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=40, detectShadows=False)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    zebra_found, stripes, zebra_top, zebra_bottom = detect_zebra(frame)

    if zebra_found:
        cv2.putText(frame, "ZEBRA CROSSING DETECTED", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 3)
        cv2.rectangle(frame, (0, zebra_top), (640, zebra_bottom), (0,255,0), 2)
    else:
        cv2.putText(frame, "NO ZEBRA CROSSING", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 3)
        cv2.imshow("Detector", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # ------------ Motion Detection (to trigger YOLO) ----------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = bg.apply(gray)
    mask = cv2.threshold(mask, 40, 255, cv2.THRESH_BINARY)[1]
    mask = cv2.dilate(mask, None, iterations=2)

    motion_amount = np.sum(mask) // 255

    if motion_amount > 1500:  # Motion detected → run YOLO
        results = model(frame, verbose=False)

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                if cls != 0:  # we only trained 'person'
                    continue

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                person_center_y = (y1 + y2) // 2

                # Decide jaywalking or safe
                if zebra_top <= person_center_y <= zebra_bottom:
                    status = "SAFE"
                    color = (0,255,0)
                else:
                    status = "JAYWALKING"
                    color = (0,0,255)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, status, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow("Detector", frame)
    if cv0.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
