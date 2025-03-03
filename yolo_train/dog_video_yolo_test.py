import cv2
from ultralytics import YOLO

# 1. 指定模型與影片的路徑
model_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\6best.pt"
video_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\dog_angry2.mp4"
output_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\output1.mp4"

# 2. 載入模型 (Ultralytics YOLO)
model = YOLO(model_path)

# 3. 開啟影片
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("無法開啟影片，請確認路徑是否正確。")
    exit()

# 4. 取得影片資訊
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 5. 建立 VideoWriter 寫出影片
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 常見於 MP4
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# 6. 逐幀處理影片，並寫入結果
while True:
    ret, frame = cap.read()
    if not ret:
        break  # 讀不到影格表示影片結束或發生問題

    # 模型推論 (只顯示類別名稱、不顯示信心指數)
    results = model.predict(
        source=frame,
        conf=0.5,
        imgsz=640,
        device='cuda:0'  # 若無 GPU，改 'cpu'
    )

    # 繪製偵測框
    boxes = results[0].boxes
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        cls = int(box.cls[0])               # 類別索引
        class_name = model.names[cls]       # 取得類別名稱

        x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
        color = (0, 255, 0)  # 綠色

        # 畫框
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        # 只顯示類別名稱 (不顯示置信度)
        cv2.putText(frame, class_name, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)

    # 寫入處理後的影格到輸出影片
    out.write(frame)

# 7. 完成後釋放資源
cap.release()
out.release()

print(f"影片處理完成，已儲存至：{output_path}")
# 程式執行完畢後會自動結束，不需要任何額外按鍵
