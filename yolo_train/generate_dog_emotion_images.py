import os
import random
import torch
from PIL import Image
from diffusers import StableDiffusion3Pipeline

def init_device():
    """
    檢查 GPU 可用狀況，回傳對應 device
    """
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print(f"目前裝置：{device}")
    return device


def load_pipeline(checkpoint, device):
    """
    載入 Stable Diffusion 3.5 Large Pipeline，並移到指定裝置
    """
    pipe = StableDiffusion3Pipeline.from_pretrained(
        checkpoint,
        torch_dtype=torch.bfloat16
    )
    pipe = pipe.to(device)
    return pipe


def get_start_index(inspect_dir, category):
    """
    從 inspection 資料夾讀取已存在檔名，計算下個編號
    """
    if not os.path.isdir(inspect_dir):
        return 1
    existing = [
        int(f.split("_")[1].split('.')[0])
        for f in os.listdir(inspect_dir)
        if f.startswith(f"{category}_") and f.endswith('.jpg')
    ]
    return max(existing, default=0) + 1


def generate_images(
    pipe, category, num, prompts, base_dir, 
    inspect_dir, target_size=(640,640)
):
    """
    針對單一類別生成多張圖片，並儲存到檢查資料夾
    """
    os.makedirs(inspect_dir, exist_ok=True)
    start_idx = get_start_index(inspect_dir, category)
    print(f"開始產生 {category} 圖片，編號從 {start_idx} 開始，共 {num} 張...")

    for i in range(num):
        prompt = random.choice(prompts)
        negative = (
            "cartoonish, distorted, blurry, unrealistic, incomplete body, cute"
        )
        # 推論
        result = pipe(
            prompt=prompt,
            negative_prompt=negative,
            guidance_scale=8.5,
            num_inference_steps=50
        )
        img = result.images[0]
        # resize
        if img.size != target_size:
            img = img.resize(target_size, Image.Resampling.LANCZOS)
        idx = start_idx + i
        out_path = os.path.join(inspect_dir, f"{category}_{idx:04d}.jpg")
        img.save(out_path)
        print(f"已存：{out_path}")


def main():
    # 基本設定
    checkpoint = "stabilityai/stable-diffusion-3.5-large"
    base_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\data\dog-emotion"
    inspect_base = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\data\generated_inspection"
    categories = {"angry":100, "happy":100, "relaxed":100}
    prompts = {
        # 依照原 prompt list 建立 dict
        "angry": [
            "a furious rottweiler snarling ... realistic, 4k, high quality",
            # 其他 prompt 簡略... 
        ],
        "happy": [
            "a joyful golden retriever with its tongue out ...",
            # ...
        ],
        "relaxed": [
            "a calm border collie lying on soft grass ...",
            # ...
        ]
    }

    device = init_device()
    pipe = load_pipeline(checkpoint, device)

    for cat, num in categories.items():
        out_dir = os.path.join(base_dir, cat)
        inspect_dir = os.path.join(inspect_base, cat)
        prompts_list = prompts.get(cat, [])
        generate_images(pipe, cat, num, prompts_list, out_dir, inspect_dir)
    print("所有圖片生成完成！")

if __name__ == '__main__':
    main()