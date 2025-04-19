import os
import cv2
import torch
from ultralytics import YOLO

def init_device():
    """
    檢查有沒有 GPU，可用就用 cuda，沒有就 fallback 到 cpu
    """
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"目前裝置：{dev}")
    return dev


def setup_output_dirs(base_dir, categories):
    """
    建立分類後圖片要存放的資料夾結構：angry, happy, other
    """
    dirs = {}
    for cat in categories:
        path = os.path.join(base_dir, cat)
        os.makedirs(path, exist_ok=True)
        dirs[cat] = path
    return dirs


def load_model(model_path):
    """
    載入 Ultralytics YOLO 模型
    """
    return YOLO(model_path)


def classify_image(model, image_path, output_dirs, device, conf=0.5, imgsz=640):
    """
    對單張圖片做推論，再依分類結果存檔到對應資料夾
    """
    # 讀圖、推論
    img = cv2.imread(image_path)
    if img is None:
        print(f"讀圖失敗：{image_path}")
        return

    results = model.predict(
        source=img,
        conf=conf,
        imgsz=imgsz,
        device=device,
        save=False
    )

    # 沒偵測到就放 other
    if not results[0].boxes:
        target_cat = 'other'
        out_img = img
        print("偵測不到目標，歸類為 other")
    else:
        # 取第一個框的類別
        cls_id = int(results[0].boxes[0].cls[0])
        cat_name = model.names.get(cls_id, 'other')
        target_cat = cat_name if cat_name in output_dirs else 'other'
        # 繪製標註
        out_img = results[0].plot()
        print(f"判斷結果：{target_cat}")

    # 儲存圖片
    fname = os.path.basename(image_path)
    save_path = os.path.join(output_dirs[target_cat], fname)
    cv2.imwrite(save_path, out_img)
    print(f"已存到：{save_path}\n")


def main():
    # 1. 初始化環境
    device = init_device()

    # 2. 設定路徑
    model_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\best.pt"
    source_image = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\data\some_dog_image.jpg"
    output_base = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\data\Dog_classified"
    categories = ['angry', 'happy', 'other']
    output_dirs = setup_output_dirs(output_base, categories)

    # 3. 載入模型
    model = load_model(model_path)

    # 4. 推論並存檔
    classify_image(model, source_image, output_dirs, device)

    print("全部處理完成！")

if __name__ == '__main__':
    main()
