import os

def find_duplicate_txt(folders):
    """
    檢查多個資料夾 (*.txt) 檔案內容是否重複，
    若發現重複，就把相同內容的檔案路徑列出來。
    """
    content_map = {}  # { 檔案內容: [檔案路徑, ...] }

    for folder in folders:
        if not os.path.isdir(folder):
            print(f"資料夾不存在，跳過：{folder}")
            continue
        # 瀏覽所有檔案
        for root, _, files in os.walk(folder):
            for fname in files:
                if not fname.lower().endswith('.txt'):
                    continue
                path = os.path.join(root, fname)
                # 讀取檔案內容，先嘗試 utf-8，失敗才用 cp950
                try:
                    text = open(path, 'r', encoding='utf-8').read()
                except UnicodeDecodeError:
                    text = open(path, 'r', encoding='cp950').read()
                except Exception as e:
                    print(f"讀檔錯誤：{path} -> {e}")
                    continue
                content_map.setdefault(text, []).append(path)

    # 列出內容重複的群組
    has_dup = False
    for text, paths in content_map.items():
        if len(paths) > 1:
            has_dup = True
            print("以下檔案內容完全一樣：")
            for p in paths:
                print("  ", p)
            print('-' * 50)

    if not has_dup:
        print("沒有找到完全重複的檔案。")


if __name__ == '__main__':
    # 要檢查的資料夾列表，請按實際需求填寫
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
    find_duplicate_txt(folders_to_check)
