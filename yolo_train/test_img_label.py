import os
import cv2

# 若要 UI 選資料夾可用 tkinter，沒裝就改用 input()
try:
    import tkinter as tk
    from tkinter import filedialog
    USE_TK = True
except ImportError:
    USE_TK = False


def select_folder(prompt="請選擇資料夾"):
    """
    用 tkinter 跳出對話框選資料夾，或 fallback 到 input()
    """
    if USE_TK:
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askdirectory(title=prompt)
        root.destroy()
        return path
    else:
        path = input(f"{prompt} (輸入路徑)：").strip()
        return path


def make_unique_dir(base_name):
    """
    建立不會覆蓋原有資料夾的唯一名稱資料夾
    e.g. base, base_1, base_2...
    """
    if not os.path.exists(base_name):
        os.makedirs(base_name)
        return base_name
    idx = 1
    while True:
        name = f"{base_name}_{idx}"
        if not os.path.exists(name):
            os.makedirs(name)
            return name
        idx += 1


def parse_yolo_line(line, img_w, img_h):
    """
    解析 YOLO 格式一行: class_id x_center y_center w h
    回傳 bbox 左上與右下座標及 class_id
    """
    parts = line.split()
    if len(parts) != 5:
        raise ValueError("格式錯誤")
    cid = int(parts[0])
    x_ctr, y_ctr, w_rel, h_rel = map(float, parts[1:])
    x_ctr *= img_w; y_ctr *= img_h
    w_rel *= img_w; h_rel *= img_h
    x1 = int(x_ctr - w_rel/2)
    y1 = int(y_ctr - h_rel/2)
    x2 = int(x_ctr + w_rel/2)
    y2 = int(y_ctr + h_rel/2)
    return x1, y1, x2, y2, cid


def process_annotations(image_folder, label_folder, output_base):
    """
    批次讀圖、畫框 (bbox) 並存檔，記錄失敗案例
    """
    # 準備 output folder
    base_name = os.path.basename(os.path.normpath(image_folder))
    out_folder = make_unique_dir(f"test_{base_name}")
    print(f"輸出資料夾：{out_folder}")

    failed = []
    # 支援常見影像格式
    exts = ('.jpg', '.jpeg', '.png', '.bmp')

    for fname in sorted(os.listdir(image_folder)):
        if not fname.lower().endswith(exts):
            continue
        img_path = os.path.join(image_folder, fname)
        img = cv2.imread(img_path)
        if img is None:
            print(f"讀不到圖片：{img_path}")
            failed.append(img_path)
            continue
        h, w = img.shape[:2]

        # 對應 YOLO annotation 檔
        label_file = os.path.splitext(fname)[0] + '.txt'
        label_path = os.path.join(label_folder, label_file)
        if not os.path.isfile(label_path):
            print(f"找不到標註檔：{label_path}")
            failed.append(img_path)
            continue

        # 讀並解析多行標註
        with open(label_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        if not lines:
            print(f"標註檔沒內容：{label_path}")
            failed.append(img_path)
            continue

        valid = False
        for line in lines:
            try:
                x1, y1, x2, y2, cid = parse_yolo_line(line, w, h)
                # 畫框與 label
                cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(img, f"ID:{cid}", (x1, y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                valid = True
            except Exception as e:
                print(f"解析錯誤 ({label_path}): {e}")
        if not valid:
            failed.append(img_path)
            continue

        # 存檔
        out_path = os.path.join(out_folder, fname)
        cv2.imwrite(out_path, img)
        print(f"已輸出：{out_path}")

    print("\n處理完畢！")
    if failed:
        print("以下檔案處理失敗：")
        for p in failed:
            print(p)


def main():
    img_dir = select_folder("請選擇圖片資料夾")
    if not img_dir:
        print("沒選圖片資料夾，結束。")
        return
    lbl_dir = select_folder("請選擇標註.txt 資料夾")
    if not lbl_dir:
        print("沒選標註資料夾，結束。")
        return
    process_annotations(img_dir, lbl_dir, None)

if __name__ == '__main__':
    main()
