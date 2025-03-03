import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image


def select_folder():
    """使用者介面選取資料夾，並回傳其路徑。"""
    root = tk.Tk()
    root.withdraw()  # 隱藏主視窗
    folder_path = filedialog.askdirectory(title="選擇要縮放圖片的資料夾")
    return folder_path


def resize_images_in_folder(folder_path, size=(640, 640)):
    """將資料夾中的所有圖片縮放成指定大小 (預設 640x640)。"""
    valid_extensions = ('.jpg', '.jpeg', '.png')

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(valid_extensions):
            file_path = os.path.join(folder_path, filename)

            with Image.open(file_path) as img:
                resized_img = img.resize(size)
                # 覆蓋原本圖片（若不想覆蓋可換路徑）
                resized_img.save(file_path)

            print(f"{filename} 已縮放成 {size[0]}x{size[1]}")


if __name__ == "__main__":
    folder_path = select_folder()
    if folder_path:
        resize_images_in_folder(folder_path, size=(640, 640))
        print("圖片縮放完成！")
    else:
        print("未選取任何資料夾。")
