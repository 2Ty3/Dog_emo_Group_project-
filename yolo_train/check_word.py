import os

# 需要檢查的資料夾清單 (請依實際需求調整)
folders_to_check = [
    r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\data\CL\an_WORD_F",
    r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\data\CL\ha_WORD_F",
    r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\data\JW\re_WORD",
    r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\data\JW\re_WORD_F",
    r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\data\Terry\ha_WORD",
    r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\data\Terry\re_WORD_F",
    r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\data\WU\an_WORD",
    r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\data\WU\an_WORD_F",
]

# 用來儲存：{ "檔案內容" : [ "檔案路徑1", "檔案路徑2", ... ] }
content_to_files = {}

for folder in folders_to_check:
    if not os.path.exists(folder):
        print(f"路徑不存在，跳過：{folder}")
        continue

    # 走訪資料夾中的所有檔案
    for root, dirs, files in os.walk(folder):
        for file in files:
            # 僅處理 .txt 檔案
            if file.lower().endswith(".txt"):
                file_path = os.path.join(root, file)

                # 讀取整份檔案內容
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # 若編碼非 utf-8，可自行調整
                    with open(file_path, "r", encoding="cp950") as f:
                        content = f.read()
                except Exception as e:
                    print(f"無法讀取檔案 {file_path}，原因: {e}")
                    continue

                # 將內容加到字典中
                if content not in content_to_files:
                    content_to_files[content] = [file_path]
                else:
                    content_to_files[content].append(file_path)

# 最後檢查是否有內容完全相同的檔案
duplicate_found = False

for content, paths in content_to_files.items():
    if len(paths) > 1:
        duplicate_found = True
        print("以下檔案內容 **完全重複**：")
        for p in paths:
            print("  ", p)
        print("-" * 60)

if not duplicate_found:
    print("未發現任何檔案內容完全相同的情況。")
