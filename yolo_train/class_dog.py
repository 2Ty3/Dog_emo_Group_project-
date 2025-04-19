import os
import shutil
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from tqdm import tqdm

def setup_dirs(dirs_dict):
    """確保所有輸出資料夾都存在"""
    for path in dirs_dict.values():
        os.makedirs(path, exist_ok=True)

def load_model(checkpoint, device):
    """載入 processor 與 model"""
    processor = AutoImageProcessor.from_pretrained(checkpoint)
    model = AutoModelForImageClassification.from_pretrained(checkpoint)
    return processor, model.to(device)

def classify_and_move(image_path, label, processor, model, output_dirs, threshold, device):
    """
    用 pretrained model 做推論，信心度低於 threshold 就搬到對應資料夾
    """
    try:
        img = Image.open(image_path).convert('RGB')
        inputs = processor(images=img, return_tensors='pt').to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits[0]
        probs = torch.softmax(logits, dim=0)
        pred_idx = torch.argmax(probs).item()
        confidence = probs[pred_idx].item()
        pred_label = model.config.id2label[pred_idx]

        if confidence < threshold:
            fname = os.path.basename(image_path)
            dest = os.path.join(output_dirs[label], f"{confidence:.2f}_{fname}")
            shutil.move(image_path, dest)
            print(f"移動: {fname} -> {label} 資料夾 (conf={confidence:.2f})")
        else:
            print(f"保留: {os.path.basename(image_path)} (預測: {pred_label}, conf={confidence:.2f})")
    except Exception as e:
        print(f"{os.path.basename(image_path)} 處理錯誤: {e}")

def main():
    # 影像資料夾路徑
    image_dirs = {
        'angry': r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\Dog_Emotion\angry",
        'happy': r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\Dog_Emotion\happy",
        'relaxed': r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\Dog_Emotion\relaxed",
        'sad': r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\Dog_Emotion\sad",
    }

    # 輸出根目錄，避免 raw string 尾斜線問題
    output_base = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\fack_dog"
    output_dirs = {k: os.path.join(output_base, k) for k in image_dirs}

    setup_dirs(output_dirs)

    # 載入模型與 Processor
    CHECKPOINT = 'wesleyacheng/dog-breeds-multiclass-image-classification-with-vit'
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    processor, model = load_model(CHECKPOINT, device)
    threshold = 0.2  # 信心度門檻

    # 遍歷並處理每個 category
    for label, img_dir in image_dirs.items():
        if not os.path.isdir(img_dir):
            print(f"{label} 資料夾不存在，跳過")
            continue
        print(f"開始處理 {label} 目錄")
        for fname in tqdm(os.listdir(img_dir), desc=label):
            if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            image_path = os.path.join(img_dir, fname)
            classify_and_move(
                image_path, label,
                processor, model, output_dirs,
                threshold, device
            )

    print('全部處理完畢！')

if __name__ == '__main__':
    main()
