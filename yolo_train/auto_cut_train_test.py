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
    seed=42,
):
    # 確認比例加起來是 1
    assert math.isclose(train_ratio + val_ratio + test_ratio, 1.0, rel_tol=1e-9), \
        "訓練/驗證/測試比例總和要是 1.0"

    random.seed(seed)  # 固定一下亂數種子，方便重現結果

    # 先把 train/val/test 的資料夾架構弄好
    for subset in ("train", "val", "test"):
        for cls in class_names:
            os.makedirs(os.path.join(output_dir, subset, cls, "images"), exist_ok=True)
            os.makedirs(os.path.join(output_dir, subset, cls, "annotations"), exist_ok=True)

    for cls in class_names:
        img_dir = os.path.join(base_data_dir, cls, f"{cls}_img")
        ann_dir = os.path.join(base_data_dir, cls, f"{cls}_word")

        if not os.path.isdir(img_dir):
            print(f"[{cls}] 找不到圖片資料夾：{img_dir}，跳過")
            continue

        imgs = [f for f in os.listdir(img_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not imgs:
            print(f"[{cls}] 圖片資料夾沒東西：{img_dir}，跳過")
            continue

        # 處理標註
        if os.path.isdir(ann_dir):
            anns = {f for f in os.listdir(ann_dir) if f.lower().endswith(".txt")}
        else:
            anns = set()

        paired = []
        if cls.lower() == "background":
            # background 不需要標註
            paired = [(img, None) for img in imgs]
        else:
            for img in imgs:
                name = os.path.splitext(img)[0] + ".txt"
                if name not in anns:
                    raise ValueError(f"[{cls}] 找不到對應註解：{name}")
                paired.append((img, name))

        random.shuffle(paired)
        n = len(paired)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)

        splits = {
            "train": paired[:n_train],
            "val": paired[n_train : n_train + n_val],
            "test": paired[n_train + n_val :],
        }

        # 把檔案複製到對應資料夾
        for subset, items in splits.items():
            for img, ann in items:
                shutil.copy(
                    os.path.join(img_dir, img),
                    os.path.join(output_dir, subset, cls, "images", img)
                )
                if ann:
                    shutil.copy(
                        os.path.join(ann_dir, ann),
                        os.path.join(output_dir, subset, cls, "annotations", ann)
                    )

        # 印一下結果，讓人一目了然
        print(f"[{cls}] 總共：{n} 張 → train {len(splits['train'])}, val {len(splits['val'])}, test {len(splits['test'])}")

    print("所有類別都處理完畢！")


if __name__ == "__main__":
    class_names = ["angry", "happy", "background"]
    base_data_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\data"
    output_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\PJ_Dog_Emotion\train"

    split_dataset(class_names, base_data_dir, output_dir)
