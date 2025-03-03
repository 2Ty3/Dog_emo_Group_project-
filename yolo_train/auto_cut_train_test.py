import os
import shutil
import random
import math


def split_dataset(
        class_names,
        base_data_dir,
        output_dir,
        train_ratio=0.7,
        val_ratio=0.2,
        test_ratio=0.1,
        seed=42
):
    """
    將多個類別的圖片與標註檔依照比例 (train_ratio, val_ratio, test_ratio) 分割，
    並將它們複製到 output_dir 下的 train/val/test 三種子資料夾中。

    - 如果某類別 (例如 background) 沒有標註資料夾 (background_word)，則不複製標註。
    - 如果某類別沒有任何圖片，則跳過該類別。
    """

    # 確認三種比例相加要等於 1.0
    assert math.isclose(train_ratio + val_ratio + test_ratio, 1.0, rel_tol=1e-9), \
        "訓練、驗證和測試比例總和必須為 1.0"

    # 設定隨機種子，確保每次分割結果相同
    random.seed(seed)

    # 預先建立 train, val, test 資料夾結構
    subsets = ["train", "val", "test"]
    for subset in subsets:
        for class_name in class_names:
            os.makedirs(os.path.join(output_dir, subset, class_name, "images"), exist_ok=True)
            os.makedirs(os.path.join(output_dir, subset, class_name, "annotations"), exist_ok=True)

    # 針對每個類別進行分割
    for class_name in class_names:
        img_dir = os.path.join(base_data_dir, class_name, f"{class_name}_img")
        ann_dir = os.path.join(base_data_dir, class_name, f"{class_name}_word")

        # 如果圖片資料夾不存在，直接跳過
        if not os.path.isdir(img_dir):
            print(f"[{class_name}] 找不到圖片資料夾：{img_dir}，跳過。")
            continue

        # 收集所有圖片檔
        image_files = [
            f for f in os.listdir(img_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if not image_files:
            print(f"[{class_name}] 圖片資料夾是空的：{img_dir}，跳過。")
            continue

        # 若標註資料夾不存在或不是資料夾，直接視為沒有標註
        if not os.path.isdir(ann_dir):
            annotation_files = []
        else:
            annotation_files = [
                f for f in os.listdir(ann_dir) if f.lower().endswith(".txt")
            ]

        # 組合圖檔與標註檔
        combined = []
        # 如果是 background，假設沒有標註
        if class_name.lower() == "background":
            for img_file in image_files:
                combined.append((img_file, None))
        else:
            # 其他類別 (angry, happy, ...) 就檢查對應 .txt
            for img_file in image_files:
                base_name = os.path.splitext(img_file)[0]
                txt_name = base_name + ".txt"
                if txt_name not in annotation_files:
                    # 如果想跳過而不拋錯，可換成 print() + continue
                    raise ValueError(f"[{class_name}] 圖片 {img_file} 找不到對應標註檔 {txt_name}")
                combined.append((img_file, txt_name))

        # 隨機打亂
        random.shuffle(combined)

        # 依比例分出 train, val, test
        total_count = len(combined)
        train_count = int(total_count * train_ratio)
        val_count = int(total_count * val_ratio)

        train_set = combined[:train_count]
        val_set = combined[train_count: train_count + val_count]
        test_set = combined[train_count + val_count:]

        # 定義複製函式
        def copy_files(file_pairs, subset_name):
            for img_file, txt_file in file_pairs:
                src_img_path = os.path.join(img_dir, img_file)
                dst_img_path = os.path.join(
                    output_dir, subset_name, class_name, "images", img_file
                )
                shutil.copy(src_img_path, dst_img_path)

                # 如果沒有標註檔 (txt_file is None)，就不複製
                if txt_file is not None:
                    src_txt_path = os.path.join(ann_dir, txt_file)
                    dst_txt_path = os.path.join(
                        output_dir, subset_name, class_name, "annotations", txt_file
                    )
                    shutil.copy(src_txt_path, dst_txt_path)

        # 開始複製
        copy_files(train_set, "train")
        copy_files(val_set, "val")
        copy_files(test_set, "test")

        # 列印分割結果
        print(f"\n分類 [{class_name}]：共 {total_count} 筆")
        print(f"  -> train: {len(train_set)} 筆")
        print(f"  -> val:   {len(val_set)} 筆")
        print(f"  -> test:  {len(test_set)} 筆")

    print("\n所有類別的資料已分割完畢！")


if __name__ == "__main__":
    # 假設 class_names 中含有 background，但 background_word 不存在
    class_names = ["angry", "happy", "background"]

    # 請依實際情況修改路徑
    base_data_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\data"
    output_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\train"

    split_dataset(
        class_names,
        base_data_dir,
        output_dir,
        train_ratio=0.7,
        val_ratio=0.2,
        test_ratio=0.1,
        seed=42
    )
