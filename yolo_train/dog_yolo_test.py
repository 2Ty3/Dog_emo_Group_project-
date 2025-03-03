import torch
import cv2
import os
from ultralytics import YOLO

# ------------------------------------------------------------
# 1. 檢查是否有 GPU，可用時指定 device='cuda'；否則使用 'cpu'
# ------------------------------------------------------------
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"目前使用裝置：{device}")

# ------------------------------------------------------------
# 2. 指定權重檔與待辨識圖片路徑
# ------------------------------------------------------------
model_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\best.pt"
source_image = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\data\some_dog_image.jpg"
output_folder = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\data\Dog_classified"

os.makedirs(os.path.join(output_folder, 'angry'), exist_ok=True)
os.makedirs(os.path.join(output_folder, 'happy'), exist_ok=True)
os.makedirs(os.path.join(output_folder, 'other'), exist_ok=True)

# ------------------------------------------------------------
# 3. 載入 YOLO 模型並移動到對應裝置 (GPU or CPU)
# ------------------------------------------------------------
model = YOLO(model_path)
# 若想手動指定 device，可再呼叫 model.model.to(device)；不過 ultralytics 也支援在 predict() 時指定 device

# ------------------------------------------------------------
# 4. 對單一圖片進行推論 (使用 GPU 加速)
# ------------------------------------------------------------
results = model.predict(
    source=source_image,  # 單一圖片
    conf=0.5,             # 信心閾值
    imgsz=640,            # 推論時輸入大小
    device=device,        # 使用 GPU (cuda) 或 CPU
    save=False
)

# 讀取原始圖片，後續用來繪製標註或直接保存
original_img = cv2.imread(source_image)

# ------------------------------------------------------------
# 5. 判斷推論結果，只顯示類別名稱 (不顯示信心指數)
# ------------------------------------------------------------
if len(results[0].boxes) > 0:
    # 取第一個偵測框
    first_box = results[0].boxes[0]
    cls = int(first_box.cls[0])
    class_name = model.names[cls]  # e.g. "angry", "happy", etc.

    # 繪製標註圖 (若不想顯示信心度，也可以自行用 cv2.rectangle + putText)
    annotated_img = results[0].plot()

    # 根據類別名稱決定輸出資料夾
    if class_name == "angry":
        save_path = os.path.join(output_folder, 'angry', os.path.basename(source_image))
    elif class_name == "happy":
        save_path = os.path.join(output_folder, 'happy', os.path.basename(source_image))
    else:
        save_path = os.path.join(output_folder, 'other', os.path.basename(source_image))

    # 儲存繪製後的圖片
    cv2.imwrite(save_path, annotated_img)
    print(f"圖片判斷結果：{class_name}，已保存至：{save_path}")

else:
    # 無法偵測到任何目標，直接歸類為 other
    save_path = os.path.join(output_folder, 'other', os.path.basename(source_image))
    cv2.imwrite(save_path, original_img)
    print("無法辨識到任何狗的情緒，已歸類為 other")
    print(f"已保存原圖至：{save_path}")
