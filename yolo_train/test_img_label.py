import os
import cv2

# 若使用 tkinter 選擇資料夾，需安裝並匯入 tkinter
try:
    import tkinter as tk
    from tkinter import filedialog
    USE_TK = True
except ImportError:
    USE_TK = False

def select_folder_with_tk(title="選擇資料夾"):
    """使用 tkinter 跳出對話框讓使用者選擇資料夾。"""
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title=title)
    root.destroy()
    return folder_selected

def make_unique_folder(folder):
    """
    若指定的 folder 名稱已存在，則在尾端自動加上遞增數字( _1, _2, ... )。
    最終回傳一個已成功建立的、不會覆蓋舊檔的資料夾路徑。
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
        return folder
    else:
        i = 1
        new_folder = f"{folder}_{i}"
        # 持續遞增，直到名稱不重複
        while os.path.exists(new_folder):
            i += 1
            new_folder = f"{folder}_{i}"
        os.makedirs(new_folder)
        return new_folder

def main():
    # ---------------------------------------------------------
    # Step 1: 互動式選擇圖片資料夾 (image_folder)
    #         互動式選擇標註.txt資料夾 (label_folder)
    # ---------------------------------------------------------
    if USE_TK:
        image_folder = select_folder_with_tk("請選擇『圖片資料夾』")
        if not image_folder:
            print("未選擇圖片資料夾，程式結束。")
            return

        label_folder = select_folder_with_tk("請選擇『標註.txt 資料夾』")
        if not label_folder:
            print("未選擇標註.txt 資料夾，程式結束。")
            return
    else:
        # 若 tkinter 無法使用，可以改用 input() 或直接寫死路徑
        image_folder = input("請輸入『圖片資料夾』的路徑：").strip()
        label_folder = input("請輸入『標註.txt 資料夾』的路徑：").strip()

        if not os.path.isdir(image_folder):
            print(f"指定的圖片資料夾不存在：{image_folder}")
            return
        if not os.path.isdir(label_folder):
            print(f"指定的標註.txt 資料夾不存在：{label_folder}")
            return

    # ---------------------------------------------------------
    # Step 2: 建立新的輸出資料夾，名稱以 "test_" 開頭
    #         若資料夾已存在，則字尾加上遞增數字
    # ---------------------------------------------------------
    base_name = os.path.basename(os.path.normpath(image_folder))  # e.g. "dog", "ha_WORD"
    desired_folder_name = f"test_{base_name}"                     # e.g. "test_dog"
    output_folder = make_unique_folder(desired_folder_name)       # 可能建立 "test_dog", "test_dog_1", ...

    print(f"圖片來源資料夾: {image_folder}")
    print(f"標註來源資料夾: {label_folder}")
    print(f"輸出資料夾: {output_folder}")
    print("開始處理...\n")

    # ---------------------------------------------------------
    # Step 3: 逐一讀取圖片，繪製標註框後輸出
    #         若有「標記失敗」，要記錄失敗的圖片路徑
    # ---------------------------------------------------------
    failed_images = []  # 用來紀錄標記失敗的圖片

    for filename in os.listdir(image_folder):
        # 判斷是否為常見的圖片格式
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
            # 3.1 圖片與標註檔路徑
            image_path = os.path.join(image_folder, filename)
            label_filename = os.path.splitext(filename)[0] + ".txt"
            label_path = os.path.join(label_folder, label_filename)

            # 3.2 讀取圖片
            image = cv2.imread(image_path)
            if image is None:
                print(f"圖片無法讀取：{image_path}")
                failed_images.append(image_path)
                continue

            # 3.3 取得圖片尺寸
            img_height, img_width = image.shape[:2]

            # 3.4 讀取對應的標註檔
            if not os.path.exists(label_path):
                print(f"找不到標註檔：{label_path}")
                failed_images.append(image_path)
                continue

            with open(label_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if len(lines) == 0:
                # 標註檔行數為 0 -> 無任何標註
                print(f"標註檔無內容：{label_path}")
                failed_images.append(image_path)
                continue

            # 用於判斷此圖片是否至少有一個有效 bbox
            valid_bbox_found = False

            # 3.5 逐行處理標註資訊
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 假設 YOLO 標註格式: class_id x_center y_center width height (共5個欄位)
                parts = line.split()
                if len(parts) != 5:
                    print(f"標註格式不符合預期: {line} (檔案：{label_path})")
                    continue

                try:
                    class_id_str, x_center_str, y_center_str, w_str, h_str = parts
                    class_id = int(class_id_str)
                    x_center = float(x_center_str) * img_width
                    y_center = float(y_center_str) * img_height
                    bbox_width = float(w_str) * img_width
                    bbox_height = float(h_str) * img_height
                except ValueError:
                    print(f"標註數值解析失敗: {line} (檔案：{label_path})")
                    continue

                # 計算左上角(x1, y1) 及右下角(x2, y2)
                x1 = int(x_center - bbox_width / 2)
                y1 = int(y_center - bbox_height / 2)
                x2 = int(x_center + bbox_width / 2)
                y2 = int(y_center + bbox_height / 2)

                # 在此也可檢查 bbox 是否完全在圖內，但示例僅繪製
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label_text = f"Class: {class_id}"
                cv2.putText(image, label_text, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                valid_bbox_found = True

            if not valid_bbox_found:
                # 代表該標註檔所有行都解析失敗 -> 視為標記失敗
                failed_images.append(image_path)
            else:
                # 3.6 存檔至輸出資料夾
                output_path = os.path.join(output_folder, filename)
                cv2.imwrite(output_path, image)
                print(f"已輸出標註後的圖片：{output_path}")

    print("\n處理完成！")
    if failed_images:
        print("以下圖片『標記失敗』或『無法繪製』，請檢查：")
        for img in failed_images:
            print(img)  # 每張失敗的圖片分行顯示
    else:
        print("沒有發現任何標記失敗的圖片。")

if __name__ == "__main__":
    main()
