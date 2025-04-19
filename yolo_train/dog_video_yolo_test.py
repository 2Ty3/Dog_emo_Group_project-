import os
import cv2
from ultralytics import YOLO

def load_model(model_path, device='cuda:0'):
    """
    載入訓練好的 YOLO 模型
    """
    os.environ['CUDA_VISIBLE_DEVICES'] = device.split(':')[-1]
    return YOLO(model_path)


def process_video(model, video_path, output_path, conf=0.5, imgsz=640, device='cuda:0'):
    """
    用 YOLO model 一帧帧偵測，畫框並輸出成新影片
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"無法開啟影片：{video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    print(f"開始處理影片，輸出到：{output_path}")
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # 影片結束

        # 推論
        results = model.predict(source=frame, conf=conf, imgsz=imgsz, device=device, verbose=False)
        boxes = results[0].boxes

        # 畫框和標籤
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            label = model.names.get(cls_id, str(cls_id))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2, cv2.LINE_AA)

        writer.write(frame)

    cap.release()
    writer.release()
    print("影片處理完成！")


def main():
    # 路徑
    model_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\6best.pt"
    video_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\dog_angry2.mp4"
    output_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\output1.mp4"

    model = load_model(model_path, device='cuda:0')
    process_video(model, video_path, output_path,
                  conf=0.5, imgsz=640, device='cuda:0')

if __name__ == '__main__':
    main()
