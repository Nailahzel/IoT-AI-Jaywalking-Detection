import cv2
import numpy as np
import os
from tqdm import tqdm

# Paths
ROOT = "PennFudanPed"
IMG_DIR = os.path.join(ROOT, "PNGImages")
MASK_DIR = os.path.join(ROOT, "PedMasks")

# Output YOLO directory
OUT_IMAGES = "yolo_dataset/images"
OUT_LABELS = "yolo_dataset/labels"

os.makedirs(OUT_IMAGES, exist_ok=True)
os.makedirs(OUT_LABELS, exist_ok=True)

for mask_name in tqdm(os.listdir(MASK_DIR)):
    if not mask_name.endswith(".png"):
        continue

    # Example: FudanPed00001_mask.png --> FudanPed00001
    base = mask_name.replace("_mask.png", "")
    mask_path = os.path.join(MASK_DIR, mask_name)
    img_path = os.path.join(IMG_DIR, base + ".png")

    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.imread(img_path)

    if img is None or mask is None:
        continue

    h, w = mask.shape

    # Multiple pedestrians → masks are encoded
    unique_ids = np.unique(mask)
    unique_ids = unique_ids[unique_ids != 0]  # skip background

    labels = []

    for uid in unique_ids:
        obj = np.where(mask == uid)
        y1, y2 = np.min(obj[0]), np.max(obj[0])
        x1, x2 = np.min(obj[1]), np.max(obj[1])

        # Convert to YOLO format
        x_center = (x1 + x2) / 2 / w
        y_center = (y1 + y2) / 2 / h
        bw = (x2 - x1) / w
        bh = (y2 - y1) / h

        labels.append(f"0 {x_center} {y_center} {bw} {bh}")

    # Save YOLO label
    with open(os.path.join(OUT_LABELS, base + ".txt"), "w") as f:
        f.write("\n".join(labels))

    # Save image
    cv2.imwrite(os.path.join(OUT_IMAGES, base + ".jpg"), img)
