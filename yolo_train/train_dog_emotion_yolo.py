import os
import json
import cv2
import torch
import matplotlib.pyplot as plt
from ultralytics import YOLO


def check_data_split(base_dir):
    """
    檢查 train/val/test 資料夾是否存在，並且裡面有圖片
    回傳 True/False
    """
    subsets = ['train', 'val', 'test']
    missing = []
    for sub in subsets:
        path = os.path.join(base_dir, sub)
        if not os.path.isdir(path):
            missing.append(f"缺資料夾: {path}")
        else:
            imgs = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.png'))]
            if not imgs:
                missing.append(f"{path} 沒圖片")
    if missing:
        print("資料結構有問題：")
        for m in missing:
            print(" -", m)
        return False
    print("資料夾檢查 OK！")
    return True


def detect_image_size(base_dir):
    """
    統計 train/val/test 下各解析度圖片數量
    回傳 dict: {(w,h): count}
    """
    subsets = ['train', 'val', 'test']
    size_counts = {}
    for sub in subsets:
        path = os.path.join(base_dir, sub)
        if not os.path.isdir(path):
            continue
        for f in os.listdir(path):
            if f.lower().endswith(('.jpg', '.png')):
                img = cv2.imread(os.path.join(path, f))
                if img is None:
                    continue
                h, w = img.shape[:2]
                size_counts[(w, h)] = size_counts.get((w, h), 0) + 1
    print("影像尺寸分布：")
    for (w, h), cnt in size_counts.items():
        print(f" - {w}x{h}: {cnt} 張")
    return size_counts


def save_training_results(results, output_dir):
    """
    儲存訓練結果：寫 JSON, loss 圖, 以及文字摘要
    """
    os.makedirs(output_dir, exist_ok=True)
    # 1. JSON
    metrics = results.metrics
    with open(os.path.join(output_dir, 'metrics.json'), 'w', encoding='utf-8') as fp:
        json.dump(metrics, fp, indent=2)

    # 2. loss plot
    epochs = list(range(1, len(metrics.get('box_loss', [])) + 1))
    plt.figure()
    plt.plot(epochs, metrics.get('box_loss', []), label='box_loss')
    plt.plot(epochs, metrics.get('cls_loss', []), label='cls_loss')
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.title('Loss over Epochs')
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'loss_curve.png'))
    plt.close()

    # 3. summary text
    summary_file = os.path.join(output_dir, 'metrics_summary.txt')
    with open(summary_file, 'w', encoding='utf-8') as fp:
        fp.write('--- 訓練結果摘要 ---\n')
        for key in ['box_loss', 'obj_loss', 'cls_loss', 'mAP50', 'mAP50-95']:
            val = metrics.get(key, 'N/A')
            fp.write(f"{key}: {val}\n")
    print(f"訓練結果已存到 {output_dir}")


def train_model(base_dir, yaml_file, output_dir):
    """
    呼叫 Ultralytics YOLO 進行訓練，並回傳結果物件
    """
    # 確保 CUDA
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA 不可用')
    device = 'cuda:0'
    os.environ['ULTRALYTICS_CACHE'] = base_dir
    model = YOLO('YOLO11m.pt')
    results = model.train(
        data=os.path.join(base_dir, yaml_file),
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
        project=output_dir,
        name='YOLO11m_LimitedGPU'
    )
    return results


def main():
    base_dir = r"C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/PJ_Dog_Emotion/1230_train"
    if not check_data_split(base_dir):
        print('先把資料夾弄好，再重來')
        return
    detect_image_size(base_dir)

    # 訓練
    results = train_model(base_dir, 'dog_emotion.yaml',
                          r"C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/PJ_Dog_Emotion/training_results")
    # 存結果
    save_training_results(results,
                          r"C:/Users/coffeetea/PycharmProjects/ptoc2.5.1/PJ_Dog_Emotion/training_results")
    print('所有步驟結束！')


if __name__ == '__main__':
    main()
