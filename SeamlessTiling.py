import torch
import numpy as np
from PIL import Image

class SeamlessTiling:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "tile_x": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 16,
                    "step": 1,
                }),
                "tile_y": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 16,
                    "step": 1,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "tile_image"
    CATEGORY = "Image Processing"

    def tile_image(self, image: torch.Tensor, tile_x: int, tile_y: int):
        # 将输入的Tensor转换为Pillow图像
        i = 255. * image.cpu().numpy().squeeze()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        
        # 获取原始图像的尺寸
        width, height = img.size
        
        # 创建一个新的空白图像，尺寸为平铺后的大小
        new_width = width * tile_x
        new_height = height * tile_y
        new_img = Image.new(img.mode, (new_width, new_height))
        
        # 循环并将原始图像粘贴到新图像的相应位置
        for x in range(tile_x):
            for y in range(tile_y):
                new_img.paste(img, (x * width, y * height))
                
        # 将处理后的Pillow图像转换回Tensor
        output_image = np.array(new_img).astype(np.float32) / 255.0
        output_tensor = torch.from_numpy(output_image).unsqueeze(0)
        
        return (output_tensor,)

# ComfyUI的节点映射
NODE_CLASS_MAPPINGS = {
    "SeamlessTiling": SeamlessTiling
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SeamlessTiling": "Seamless Texture Tiling"
}