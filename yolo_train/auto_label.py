import os
import cv2
import pandas as pd
from ultralytics import YOLO
from tqdm import tqdm
import logging

def main():
    # 把 ultralytics 的 log 關掉，不要一直跳出雜訊
    logging.getLogger("ultralytics").setLevel(logging.ERROR)

    # 路徑設定
    images_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\Dog Emotion"
    annotations_dir = os.path.join(images_dir, "annotations")
    labels_csv = os.path.join(images_dir, "labels.csv")
    os.makedirs(annotations_dir, exist_ok=True)

    # 支援圖片副檔名
    exts = (".jpg", ".jpeg", ".png")

    # 載入 YOLO 模型
    model = YOLO(r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\yolo11s.pt")

    # 讀取 labels.csv
    df = pd.read_csv(labels_csv)

    # 檢查有沒有新的圖檔要加到 CSV
    new_entries = []
    for cat in ["angry", "happy", "relaxed", "sad"]:
        cat_dir = os.path.join(images_dir, cat)
        if not os.path.isdir(cat_dir):
            print(f"[{cat}] 資料夾不存在，跳過檢查")
            continue
        for fname in os.listdir(cat_dir):
            if fname.lower().endswith(exts) and fname not in df["filename"].values:
                new_entries.append({"filename": fname, "label": cat})
    if new_entries:
        df = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
        df.to_csv(labels_csv, index=False)
        print(f"新增 {len(new_entries)} 張圖片到 labels.csv")

    # 紀錄哪些圖片沒辦法成功標註
    counts = {cat: 0 for cat in ["angry", "happy", "relaxed", "sad"]}

    # 開始處理每一張圖
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="處理圖片中"):  # 迴圈跑太慢再想辦法優化
        fname, cat = row["filename"], row["label"]
        img_path = os.path.join(images_dir, cat, fname)
        ann_path = os.path.join(annotations_dir, f"{os.path.splitext(fname)[0]}.txt")

        # 圖片不存在就跳過
        if not os.path.isfile(img_path):
            counts[cat] += 1
            continue

        img = cv2.imread(img_path)
        if img is None:
            counts[cat] += 1
            os.remove(img_path)
            if os.path.isfile(ann_path):
                os.remove(ann_path)
            continue

        # YOLO 推論 (confidence & IoU thresholds 可自行調整)
        results = model(img, conf=0.3, iou=0.4, verbose=False)
        boxes = results[0].boxes
        if not boxes:
            counts[cat] += 1
            os.remove(img_path)
            if os.path.isfile(ann_path):
                os.remove(ann_path)
            continue

        # 把偵測到的框寫成 YOLO 格式
        with open(ann_path, "w") as f:
            h, w = img.shape[:2]
            for box in boxes:
                x, y, bw, bh = box.xywh.cpu().numpy().flatten()
                cid = int(box.cls.cpu().numpy().item())
                # 正規化
                x /= w; y /= h; bw /= w; bh /= h
                f.write(f"{cid} {x:.6f} {y:.6f} {bw:.6f} {bh:.6f}\n")

    # 最後結果
    print("無法標註的圖片數量：")
    for cat, cnt in counts.items():
        print(f"{cat}：{cnt} 張")
    print("labels.csv 已更新完成！")

if __name__ == "__main__":
    main()
