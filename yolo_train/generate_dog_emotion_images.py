from diffusers import StableDiffusion3Pipeline
import torch
from PIL import Image
import os
import random

# 使用 GPU 或 CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 載入 Stable Diffusion 3.5 Large 模型
pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3.5-large",
    torch_dtype=torch.bfloat16
).to(device)

# 設置輸出資料夾
output_base_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\data\dog-emotion"
inspection_base_dir = r"C:\Users\coffeetea\PycharmProjects\ptoc2.5.1\data\generated_inspection"

categories = {
    "angry": 100,
    "happy": 100,
    "relaxed": 100
}

# 更新後的 Prompts
prompts = {
    "angry": [
        "a furious rottweiler snarling with curled lips and sharp, white teeth, hackles raised, bloodshot eyes, and tense muscles, full body visible, standing on a dirt road in a shadowy environment, hyper-realistic, 4k, high quality",
        "an enraged german shepherd growling menacingly, sharp fangs bared, tail stiff, tense stance, hackles raised, full body visible in an urban alley at night, hyper-realistic, 4k, high quality",
        "a hostile pit bull growling aggressively, teeth exposed naturally, tail raised, muscles flexed, full body visible on a gravel path surrounded by trash, hyper-realistic, 4k, high quality",
        "an angry stray dog with sharp teeth bared, hackles raised, tense muscles, standing aggressively on a dirt road, full body visible, realistic, 4k, high quality"
    ],
    "happy": [
        "a joyful golden retriever with its tongue out, tail wagging, and a big smile, standing in a sunny park, full body visible, hyper-realistic, 4k, high quality",
        "a playful labrador running on green grass, tongue out, tail wagging happily, full body visible, realistic, 4k, high quality",
        "a cheerful beagle standing in a garden, tongue sticking out, tail raised, smiling, full body visible, hyper-realistic, 4k, high quality"
    ],
    "relaxed": [
        "a calm border collie lying on soft grass, eyes closed, tail resting on the ground, full body visible, hyper-realistic, 4k, high quality",
        "a relaxed husky lying on a porch, eyes closed, mouth shut, tail relaxed, full body visible, realistic, 4k, high quality",
        "a peaceful german shepherd resting on a dirt trail, eyes closed, full body visible, hyper-realistic, 4k, high quality"
    ]
}


# 獲取起始圖片編號
def get_start_index(output_dir, category):
    files = os.listdir(output_dir)
    indices = [
        int(f.split("_")[1].split(".")[0])  # 提取數字部分
        for f in files if f.startswith(category) and f.endswith(".jpg")
    ]
    return max(indices, default=0) + 1


# 生成圖片
def generate_images(category, num_images, prompts, output_dir, inspection_dir, target_size=(640, 640)):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(inspection_dir, exist_ok=True)
    start_index = get_start_index(inspection_dir, category)

    print(f"開始生成 {category} 圖片，從編號 {start_index} 開始...")

    for i in range(num_images):
        prompt = random.choice(prompts)
        negative_prompt = (
            "cartoonish, distorted, blurry, unrealistic, tongue visible (if not happy), incomplete body, cute, smiling"
        )

        # 生成圖片
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            guidance_scale=8.5,
            num_inference_steps=50
        ).images[0]

        # 調整圖片大小
        if image.size != target_size:
            image = image.resize(target_size, Image.Resampling.LANCZOS)

        # 保存圖片
        current_index = start_index + i
        inspection_path = os.path.join(inspection_dir, f"{category}_{current_index:04d}.jpg")
        image.save(inspection_path)
        print(f"已保存檢查圖片：{inspection_path}")


# 主程式執行
if __name__ == "__main__":
    target_size = (640, 640)

    for category, num_images in categories.items():
        output_dir = os.path.join(output_base_dir, category)
        inspection_dir = os.path.join(inspection_base_dir, category)
        generate_images(category, num_images, prompts[category], output_dir, inspection_dir, target_size)

    print("圖片生成完成！")
