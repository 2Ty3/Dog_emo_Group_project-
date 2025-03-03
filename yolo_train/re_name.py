import os

# 若使用 tkinter 選擇資料夾 (可改用 input())
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

def main():
    # ---------------------------------------------------------
    # 1. 使用者指定「要改名的資料夾」
    # ---------------------------------------------------------
    if USE_TK:
        target_dir = select_folder_with_tk("請選擇要改名的資料夾")
        if not target_dir:
            print("未選擇資料夾，程式結束。")
            return
    else:
        target_dir = input("請輸入要改名的資料夾路徑：").strip()
        if not os.path.isdir(target_dir):
            print(f"指定資料夾不存在：{target_dir}")
            return

    # ---------------------------------------------------------
    # 2. 輸入命名前綴(prefix)、編號起始值(start)、結束值(end)
    # ---------------------------------------------------------
    prefix = input("請輸入命名前綴 (例如 happy, angry, relaxed... )：").strip()
    if not prefix:
        print("未輸入前綴，程式結束。")
        return

    try:
        start_str = input("請輸入編號起始值 (例如 1)：").strip()
        end_str   = input("請輸入編號結束值 (例如 250)：").strip()
        start = int(start_str)
        end_  = int(end_str)
        if start < 1 or end_ < start:
            print("範圍不合理，程式結束。")
            return
    except ValueError:
        print("起始值或結束值必須為整數，程式結束。")
        return

    print(f"\n您選擇的資料夾：{target_dir}")
    print(f"前綴：{prefix}")
    print(f"編號範圍：{start} ~ {end_}")
    print("開始檢查並改名...\n")

    # ---------------------------------------------------------
    # 3. 取得資料夾內所有檔案，並排序
    # ---------------------------------------------------------
    files = [f for f in os.listdir(target_dir) if f.lower().endswith(('.jpg', '.txt'))]
    files.sort()  # 預設字母排序

    if not files:
        print("資料夾中沒有符合 (.jpg, .txt) 的檔案可改名。")
        return

    # ---------------------------------------------------------
    # 4. 檢查並改名
    # ---------------------------------------------------------
    current_num = start
    renamed_count = 0
    skipped_count = 0

    for file in files:
        old_path = os.path.join(target_dir, file)
        name, ext = os.path.splitext(file)

        # 預計正確的檔名
        expected_name = f"{prefix}_{current_num:04d}{ext.lower()}"
        expected_path = os.path.join(target_dir, expected_name)

        if file == expected_name:
            # 如果檔案名稱已正確，跳過
            print(f"[跳過] 檔案名稱正確：{file}")
            skipped_count += 1
        else:
            # 如果名稱不正確，進行改名
            os.rename(old_path, expected_path)
            print(f"[改名] {file} -> {expected_name}")
            renamed_count += 1

        # 更新編號
        current_num += 1

        # 如果超出目標範圍，停止處理
        if current_num > end_:
            print("已達設定的結束範圍，停止改名。")
            break

    # ---------------------------------------------------------
    # 5. 結果總結
    # ---------------------------------------------------------
    print("\n----------------- 改名結果 -----------------")
    print(f"成功改名：{renamed_count} 個")
    print(f"跳過：{skipped_count} 個 (檔案名稱已正確)")
    if current_num <= end_:
        not_used = (end_ - current_num + 1)
        print(f"尚有 {not_used} 個編號未使用 (檔案數不足)。")
    else:
        print("所有編號已用完。")

    print("處理完成！")

if __name__ == "__main__":
    main()
