import os
import tensorflow as tf
import tensorflowjs as tfjs
from ultralytics import YOLO

def ensure_dir(path):
    """
    確保資料夾存在，若不存在就新建
    """
    os.makedirs(path, exist_ok=True)
    return path


def load_yolo(model_path):
    """
    載入 Ultralytics YOLO 模型
    """
    print("載入 YOLO 模型...", model_path)
    return YOLO(model_path)


def export_to_tf(model, saved_model_dir, imgsz=640):
    """
    匯出為 TensorFlow SavedModel
    """
    print(f"匯出到 SavedModel：{saved_model_dir}")
    model.export(format='tf', imgsz=imgsz)
    print("SavedModel 匯出完成。")


def convert_to_tflite(saved_model_dir, tflite_path):
    """
    將 SavedModel 轉成 TFLite 並存檔
    """
    print("開始轉換成 TFLite 格式...")
    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
    tflite_model = converter.convert()
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    print(f"TFLite 模型已儲存：{tflite_path}")


def convert_to_tfjs(saved_model_dir, tfjs_dir):
    """
    將 SavedModel 轉成 TensorFlow.js 格式
    """
    print("開始轉換成 TF.js 格式...")
    tfjs.converters.convert_tf_saved_model(saved_model_dir, tfjs_dir)
    print(f"TF.js 模型已儲存：{tfjs_dir}")


def main():
    # 路徑設定
    yolo_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\best.pt"
    saved_dir = ensure_dir(r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\saved_model")
    tflite_path = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\model.tflite"
    tfjs_dir = ensure_dir(r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\tfjs_model")

    # 1. 載入模型
    model = load_yolo(yolo_path)
    # 2. 匯出 SavedModel
    export_to_tf(model, saved_dir)
    # 3. 轉 TFLite
    convert_to_tflite(saved_dir, tflite_path)
    # 4. 轉 TF.js
    convert_to_tfjs(saved_dir, tfjs_dir)

    print("所有格式轉換完成！")

if __name__ == '__main__':
    main()
