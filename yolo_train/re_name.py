import os

# 嘗試用 tkinter 讓使用者選資料夾，沒裝就改用 input()
try:
    import tkinter as tk
    from tkinter import filedialog
    USE_TK = True
except ImportError:
    USE_TK = False


def select_folder():
    """
    用對話框選資料夾，回傳路徑，沒選就回空字串
    """
    if not USE_TK:
        return ''
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="請選擇要改名的資料夾")
    root.destroy()
    return folder


def get_target_dir():
    """
    取得要改名的資料夾路徑
    """
    if USE_TK:
        path = select_folder()
        if not path:
            print("你沒選資料夾，程式先結束。")
            exit()
    else:
        path = input("請輸入要改名的資料夾路徑：").strip()
        if not os.path.isdir(path):
            print(f"指定的資料夾不存在：{path}")
            exit()
    return path


def get_prefix_and_range():
    """
    讓使用者輸入前綴、起始編號和結束編號，並做基本檢查
    """
    prefix = input("輸入命名前綴 (ex: happy, angry)：").strip()
    if not prefix:
        print("要有前綴啦，程式結束。")
        exit()

    try:
        start = int(input("編號從哪開始？(整數)：").strip())
        end_ = int(input("編號到哪？(整數)：").strip())
        if start < 1 or end_ < start:
            raise ValueError
    except ValueError:
        print("編號範圍有問題，程式結束。")
        exit()

    return prefix, start, end_


def rename_files(target_dir, prefix, start, end_):
    """
    針對指定範圍的檔案做批次改名
    """
    # 抓 .jpg 跟 .txt，排好序
    files = sorted(
        f for f in os.listdir(target_dir)
        if f.lower().endswith(('.jpg', '.txt'))
    )
    if not files:
        print("這資料夾裡面沒 jpg 或 txt 檔，沒東西可改名。")
        return 0, 0, end_ - start + 1

    cur = start
    renamed = 0
    skipped = 0

    for fname in files:
        if cur > end_:
            print("超出設定範圍，停止改名。")
            break

        old = os.path.join(target_dir, fname)
        name, ext = os.path.splitext(fname)
        new_fname = f"{prefix}_{cur:04d}{ext.lower()}"
        new = os.path.join(target_dir, new_fname)

        if fname == new_fname:
            print(f"[跳過] 已經是正確名稱：{fname}")
            skipped += 1
        else:
            os.rename(old, new)
            print(f"[改名] {fname} -> {new_fname}")
            renamed += 1

        cur += 1

    unused = max(0, end_ - cur + 1)
    return renamed, skipped, unused


def main():
    target_dir = get_target_dir()
    prefix, start, end_ = get_prefix_and_range()

    print(f"目標資料夾：{target_dir}")
    print(f"前綴：{prefix}，編號範圍：{start} ~ {end_}\n")

    renamed, skipped, unused = rename_files(target_dir, prefix, start, end_)

    print("\n===== 改名結果 =====")
    print(f"成功改名：{renamed} 個")
    print(f"跳過：{skipped} 個 (已經符合命名)")
    print(f"未使用編號：{unused} 個")
    print("全部結束！")

if __name__ == '__main__':
    main()
