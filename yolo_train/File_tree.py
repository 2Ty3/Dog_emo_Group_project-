import os

def print_all_paths(root_dir, indent=''):
    """
    列印資料夾內所有檔案/子資料夾的完整路徑，
    並用縮排顯示階層結構。
    """
    try:
        entries = sorted(os.listdir(root_dir))
    except FileNotFoundError:
        print(f"找不到資料夾：{root_dir}")
        return
    except PermissionError:
        print(f"無法存取資料夾：{root_dir}")
        return

    for name in entries:
        path = os.path.join(root_dir, name)
        print(f"{indent}{path}")  # 列出完整路徑
        if os.path.isdir(path):
            # 下一層縮排再印一次
            print_all_paths(path, indent + '    ')


def main():
    # 要列印的資料夾，請自行修改
    target_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\llmtools_7b2bit_finetune"
    print(f"從這裡開始：{target_dir}")
    print_all_paths(target_dir)

if __name__ == '__main__':
    main()
