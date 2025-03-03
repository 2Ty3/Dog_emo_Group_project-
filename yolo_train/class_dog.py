import os
import shutil
from PIL import Image
import torch
from torchvision.transforms import ToTensor, Normalize, Compose
from transformers import AutoImageProcessor, AutoModelForImageClassification

# 更新的輸入與輸出路徑
image_dirs = {
    "angry": "C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/Dog_Emotion/angry",
    "happy": "C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/Dog_Emotion/happy",
    "relaxed": "C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/Dog_Emotion/relaxed",
    "sad": "C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/Dog_Emotion/sad",
}
output_dirs = {
    "angry": "C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/fack_dog/angry",
    "happy": "C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/fack_dog/happy",
    "relaxed": "C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/fack_dog/relaxed",
    "sad": "C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/fack_dog/sad",
}

# 確保輸出目錄存在
for output_dir in output_dirs.values():
    os.makedirs(output_dir, exist_ok=True)

# 模型與處理器
CHECKPOINT = "wesleyacheng/dog-breeds-multiclass-image-classification-with-vit"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
image_processor = AutoImageProcessor.from_pretrained(CHECKPOINT)
model = AutoModelForImageClassification.from_pretrained(CHECKPOINT).to(device)

# 設定置信度閾值
CONFIDENCE_THRESHOLD = 0.2

# 圖片預處理器（不改變圖片像素大小）
preprocess = Compose([
    ToTensor(),
    Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

def process_images_in_dir(image_dir, label):
    """處理特定目錄下的圖片"""
    for image_name in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_name)
        try:
            # 加載圖片
            image = Image.open(image_path).convert("RGB")

            # 預處理圖片
            inputs = preprocess(image).unsqueeze(0).to(device)

            # 模型推論
            with torch.no_grad():
                inputs_dict = image_processor(images=image, return_tensors="pt").to(device)
                outputs = model(**inputs_dict)
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()
            predicted_class_label = model.config.id2label[predicted_class_idx]
            confidence = torch.softmax(logits, dim=-1)[0][predicted_class_idx].item()

            # 檢查是否移動圖片
            if confidence < CONFIDENCE_THRESHOLD:
                move_image_to_output(image_path, label, confidence)
            else:
                print(f"保持圖片: {image_path}, 預測品種: {predicted_class_label}, 置信度: {confidence:.2f}")

        except Exception as e:
            print(f"處理圖片時發生錯誤: {image_path}, 錯誤: {str(e)}")

def move_image_to_output(image_path, label, confidence):
    """將圖片移動到對應的輸出目錄"""
    filename = os.path.basename(image_path)
    target_path = os.path.join(output_dirs[label], f"{confidence:.2f}_{filename}")
    shutil.move(image_path, target_path)
    print(f"已移動圖片: {image_path} -> {target_path}")

def main():
    for label, image_dir in image_dirs.items():
        print(f"處理目錄: {image_dir}")
        process_images_in_dir(image_dir, label)
    print("處理完成！")

if __name__ == "__main__":
    main()
