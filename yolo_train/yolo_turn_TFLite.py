import os
from ultralytics import YOLO

# 檢查並安裝必要的套件
try:
    import tensorflow as tf
except ImportError:
    raise ImportError("TensorFlow 未安裝，請執行: pip install tensorflow")

try:
    import tensorflowjs as tfjs
except ImportError:
    raise ImportError("TensorFlow.js 未安裝，請執行: pip install tensorflowjs")

# 模型路徑和匯出目標路徑
yolo_model_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\best.pt"
saved_model_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\saved_model"
tflite_model_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\model.tflite"
tfjs_model_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\tfjs_model"

# 確保目標目錄存在
os.makedirs(saved_model_dir, exist_ok=True)
os.makedirs(tfjs_model_dir, exist_ok=True)

try:
    # 1. 載入 YOLO 模型
    print("Loading YOLO model...")
    model = YOLO(yolo_model_path)

    # 2. 匯出模型為 TensorFlow SavedModel 格式
    print("Exporting to TensorFlow SavedModel format...")
    model.export(format="tf", imgsz=640)  # imgsz 根據你的模型設定調整，通常是 640x640
    print(f"TensorFlow SavedModel exported to: {saved_model_dir}")

    # 3. 轉換 SavedModel 為 TFLite 格式
    print("Converting to TFLite format...")
    # 加載 TensorFlow SavedModel
    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
    tflite_model = converter.convert()

    # 儲存 TFLite 模型
    with open(tflite_model_path, "wb") as f:
        f.write(tflite_model)
    print(f"TFLite model saved at: {tflite_model_path}")

    # 4. 轉換 SavedModel 為 TensorFlow.js 格式
    print("Converting to TensorFlow.js format...")
    tfjs.converters.convert_tf_saved_model(saved_model_dir, tfjs_model_dir)
    print(f"TensorFlow.js model saved at: {tfjs_model_dir}")

    print("Model conversion complete!")

except Exception as e:
    print(f"An error occurred: {e}")
