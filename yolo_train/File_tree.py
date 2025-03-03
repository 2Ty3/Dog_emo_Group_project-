import os

def print_all_paths(dir_path):
    # 取得該目錄下所有檔案與資料夾名稱，排序後輸出更整齊
    entries = sorted(os.listdir(dir_path))
    for entry in entries:
        full_path = os.path.join(dir_path, entry)
        print(full_path)  # 印出完整路徑
        # 若為資料夾則遞迴列印裡面的項目
        if os.path.isdir(full_path):
            print_all_paths(full_path)

if __name__ == "__main__":
    # 設定目標資料夾，請依實際路徑修改
    target_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\llmtools_7b2bit_finetune"
    # 印出主目錄的完整路徑
    print(target_dir)
    print_all_paths(target_dir)
