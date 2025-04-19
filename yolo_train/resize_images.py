import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image

def select_folder():
    """
    跳出視窗讓使用者選資料夾，回傳路徑
    """
    root = tk.Tk()
    root.withdraw()  # 收起主視窗
    path = filedialog.askdirectory(title="選擇要縮放圖片的資料夾")
    root.destroy()
    return path


def resize_images(folder_path, size=(640, 640)):
    """
    把指定資料夾裡的所有 jpg/jpeg/png 影像都縮成給定大小，並蓋掉原圖
    """
    exts = ('.jpg', '.jpeg', '.png')
    files = sorted(f for f in os.listdir(folder_path) if f.lower().endswith(exts))
    if not files:
        print("資料夾裡沒有符合的影像，請確認路徑和副檔名。")
        return

    for fname in files:
        path = os.path.join(folder_path, fname)
        try:
            with Image.open(path) as img:
                img = img.resize(size, Image.Resampling.LANCZOS)
                img.save(path)
            print(f"{fname} → {size[0]}x{size[1]} 完成")
        except Exception as e:
            print(f"縮放失敗：{fname}，原因：{e}")


def main():
    # 取得資料夾路徑
    folder = select_folder()
    if not folder:
        print("沒有選資料夾，程式先結束。")
        return

    print(f"開始縮放資料夾：{folder}")
    resize_images(folder, size=(640, 640))
    print("圖片縮放搞定！")

if __name__ == '__main__':
    main()
