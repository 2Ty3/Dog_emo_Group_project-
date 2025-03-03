import os
import json
import cv2
import torch
import matplotlib.pyplot as plt
from ultralytics import YOLO

def check_data_split(base_dir):
    subsets = ["train", "val", "test"]
    errors = []

    for subset in subsets:
        subset_path = os.path.join(base_dir, subset)
        if not os.path.exists(subset_path):
            errors.append(f"缺少目錄: {subset_path}")
            continue

        files = sorted(os.listdir(subset_path))
        image_files = [f for f in files if f.lower().endswith((".jpg", ".png"))]

        if not image_files:
            errors.append(f"目錄 {subset_path} 中沒有找到圖片文件。")

    if errors:
        print("\n發現以下問題：")
        for err in errors:
            print(err)
        return False
    else:
        print("數據結構正確。")
        return True

def detect_image_size(base_dir):
    subsets = ["train", "val", "test"]
    sizes = {}

    for subset in subsets:
        subset_path = os.path.join(base_dir, subset)
        if not os.path.exists(subset_path):
            continue

        for file in os.listdir(subset_path):
            if file.lower().endswith((".jpg", ".png")):
                full_path = os.path.join(subset_path, file)
                img = cv2.imread(full_path)
                if img is not None:
                    size = (img.shape[1], img.shape[0])
                    sizes[size] = sizes.get(size, 0) + 1

    print("圖像尺寸分佈:")
    for size, count in sizes.items():
        print(f"尺寸: {size}, 數量: {count}")

    return sizes

def save_training_results(results, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    metrics_path = os.path.join(output_dir, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(results.metrics, f, indent=4)

    epochs = range(1, len(results.metrics.get('box_loss', [])) + 1)
    plt.figure()
    plt.plot(epochs, results.metrics.get('box_loss', []), label='Box Loss')
    plt.plot(epochs, results.metrics.get('cls_loss', []), label='Class Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Loss Metrics Over Epochs')
    plt.savefig(os.path.join(output_dir, "loss_plot.png"))
    plt.close()

    metrics_text_path = os.path.join(output_dir, "metrics_summary.txt")
    with open(metrics_text_path, "w", encoding="utf-8") as f:
        f.write("--- 訓練觀察與優化建議 ---\n")
        f.write(f"Box Loss: {results.metrics.get('box_loss', 'N/A')}\n")
        f.write(f"Object Loss: {results.metrics.get('obj_loss', 'N/A')}\n")
        f.write(f"Class Loss: {results.metrics.get('cls_loss', 'N/A')}\n")
        f.write(f"mAP50: {results.metrics.get('mAP50', 'N/A')}%\n")
        f.write(f"mAP50-95: {results.metrics.get('mAP50-95', 'N/A')}%\n")

    print(f"訓練結果已保存至 {output_dir}")

if __name__ == "__main__":
    base_dir = r"C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/PJ_Dog_Emotion/1230_train"

    if not check_data_split(base_dir):
        print("請修正數據結構後再進行訓練。")
        exit()

    detect_image_size(base_dir)

    if not torch.cuda.is_available():
        raise EnvironmentError("CUDA 不可用，請檢查您的 GPU 或 CUDA 驅動。")
    device = torch.device("cuda:0")

    os.environ["ULTRALYTICS_CACHE"] = base_dir

    model = YOLO("YOLO11m.pt")

    results = model.train(
        data=os.path.join(base_dir, "dog_emotion.yaml"),
        epochs=500,
        batch=8,
        imgsz=640,
        device=device,
        lr0=0.002,
        lrf=0.01,
        mosaic=0.5,
        mixup=0.2,
        dropout=0.2,
        patience=100,
        project="DogEmotionTrain",
        name="YOLO11m_LimitedGPU",
    )

    output_dir = r"C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/PJ_Dog_Emotion/training_results"
    save_training_results(results, output_dir)

    print("\n--- 訓練觀察與優化建議 ---")
    print(f"Box Loss: {results.metrics.get('box_loss', 'N/A')}")
    print(f"Object Loss: {results.metrics.get('obj_loss', 'N/A')}")
    print(f"Class Loss: {results.metrics.get('cls_loss', 'N/A')}")
    print(f"mAP50: {results.metrics.get('mAP50', 'N/A')}%")
    print(f"mAP50-95: {results.metrics.get('mAP50-95', 'N/A')}%")

    print("\n訓練完成！結果已保存。")
