import os
import cv2
import pandas as pd
from ultralytics import YOLO
from tqdm import tqdm
import logging

# Suppress YOLO logging
logging.getLogger("ultralytics").setLevel(logging.ERROR)

# Paths
images_dir = "C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/Dog Emotion"
annotations_dir = os.path.join(images_dir, "annotations")
labels_csv_path = os.path.join(images_dir, "labels.csv")
os.makedirs(annotations_dir, exist_ok=True)

# Supported image extensions
image_extensions = (".jpg", ".jpeg", ".png")

# Load YOLO model
model = YOLO("C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/yolo11s.pt")

# Load labels.csv
labels_df = pd.read_csv(labels_csv_path)

# Check for new images
new_entries = []
for category in ["angry", "happy", "relaxed", "sad"]:
    category_dir = os.path.join(images_dir, category)
    for file in os.listdir(category_dir):
        if file.lower().endswith(image_extensions):
            if file not in labels_df['filename'].values:
                new_entries.append({"filename": file, "label": category})

# Add new entries to labels.csv
if new_entries:
    new_entries_df = pd.DataFrame(new_entries)
    labels_df = pd.concat([labels_df, new_entries_df], ignore_index=True)
    print(f"Added {len(new_entries)} new images to labels.csv.")

# Initialize counters
category_counts = {"angry": 0, "happy": 0, "relaxed": 0, "sad": 0}  # Track counts for missing annotations

# Process each image
for index, row in tqdm(labels_df.iterrows(), total=len(labels_df), desc="Processing images"):
    filename = row['filename']
    label = row['label']
    image_path = os.path.join(images_dir, label, filename)
    annotation_path = os.path.join(annotations_dir, f"{os.path.splitext(filename)[0]}.txt")

    # Check if image exists
    if not os.path.exists(image_path):
        category_counts[label] += 1
        labels_df.drop(index, inplace=True)
        continue

    # Load image
    image = cv2.imread(image_path)
    if image is None:
        category_counts[label] += 1
        labels_df.drop(index, inplace=True)
        os.remove(image_path)  # Delete image
        if os.path.exists(annotation_path):
            os.remove(annotation_path)  # Delete annotation file if exists
        continue

    # Run YOLO inference
    results = model(image, conf=0.3, iou=0.4, verbose=False)  # Adjust confidence and IoU thresholds

    # Check detections
    detections = results[0].boxes
    if detections is None or len(detections) == 0:
        category_counts[label] += 1
        labels_df.drop(index, inplace=True)
        os.remove(image_path)  # Delete image
        if os.path.exists(annotation_path):
            os.remove(annotation_path)  # Delete annotation file if exists
        continue

    # Write annotations
    with open(annotation_path, "w") as f:
        for detection in detections:
            x_center, y_center, width, height = detection.xywh.cpu().numpy().flatten()
            class_id = int(detection.cls.cpu().numpy().item())

            # Normalize coordinates
            x_center /= image.shape[1]
            y_center /= image.shape[0]
            width /= image.shape[1]
            height /= image.shape[0]

            # Write in YOLO format
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

# Save updated labels.csv
labels_df.to_csv(labels_csv_path, index=False)

# Final summary in console
print("Final counts of images that could not be annotated:")
for category, count in category_counts.items():
    print(f"{category.capitalize()}: {count} images")
print(f"labels.csv has been updated.")