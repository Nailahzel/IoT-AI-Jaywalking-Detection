from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # small & fast

model.train(
    data="data.yaml",
    epochs=50,
    imgsz=640,
    batch=8,
)
