import torch
import numpy as np
import cv2

class Onion_ImageMaskingProcessor:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "开启描边": ("BOOLEAN", {"default": True, "label_on": "开启", "label_off": "关闭"}),
                "开启蒙版": ("BOOLEAN", {"default": True, "label_on": "开启", "label_off": "关闭"}),
                "描边宽度": ("INT", {"default": 5, "min": 1, "max": 100, "step": 1, "display": "slider"}),
                "描边颜色": (["红色", "绿色", "蓝色", "白色", "黑色", "灰色", "黄色", "青色", "洋红"], {"default": "红色"}),
                "描边不透明度": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.1, "display": "slider"}),
                "蒙版颜色": (["红色", "绿色", "蓝色", "白色", "黑色", "灰色", "黄色", "青色", "洋红"], {"default": "红色"}),
                "蒙版不透明度": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.1, "display": "slider"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "run"
    CATEGORY = "Onionman"

    def run(self, image, mask, 开启描边, 开启蒙版, 描边宽度, 描边颜色, 描边不透明度, 蒙版颜色, 蒙版不透明度):
        
        # 1. 安全检查
        if not 开启描边 and not 开启蒙版:
            raise ValueError("❌ [Onionman] 错误：请至少选择一个模式（描边或蒙版）！")
        if mask is None:
            raise ValueError("❌ [Onionman] 错误：请接入遮罩！")

        # 2. 颜色定义
        colors_rgb = {
            "红色": (255, 0, 0), "绿色": (0, 255, 0), "蓝色": (0, 0, 255),
            "白色": (255, 255, 255), "黑色": (0, 0, 0), "灰色": (128, 128, 128),
            "黄色": (255, 255, 0), "青色": (0, 255, 255), "洋红": (255, 0, 255)
        }

        result_images = []
        
        for i in range(len(image)):
            # 图片转换
            img_np = (image[i].cpu().numpy() * 255).astype(np.uint8)
            if img_np.shape[2] == 1:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2RGB)
            h, w = img_np.shape[:2]

            # 遮罩转换
            current_mask = mask[i] if len(mask.shape) == 3 else mask
            mask_np = (current_mask.cpu().numpy() * 255).astype(np.uint8)
            if mask_np.shape != (h, w):
                mask_np = cv2.resize(mask_np, (w, h), interpolation=cv2.INTER_NEAREST)

            # --- 修复 1：强制二值化与闭运算（解决蒙版内部重叠痕迹问题） ---
            _, mask_np = cv2.threshold(mask_np, 127, 255, cv2.THRESH_BINARY)
            closing_kernel = np.ones((5, 5), np.uint8) 
            mask_np = cv2.morphologyEx(mask_np, cv2.MORPH_CLOSE, closing_kernel)

            # 初始化绘图层
            draw_layer = np.zeros_like(img_np)
            alpha_layer = np.zeros((h, w), dtype=np.float32)

            if 开启蒙版:
                color = colors_rgb.get(蒙版颜色, (255, 0, 0))
                draw_layer[mask_np > 0] = color
                alpha_layer[mask_np > 0] = 蒙版不透明度

            if 开启描边:
                color = colors_rgb.get(描边颜色, (255, 0, 0))
                kernel = np.ones((描边宽度, 描边宽度), np.uint8)
                
                # 计算外描边 (Dilate - Original)
                dilated = cv2.dilate(mask_np, kernel, iterations=1)
                outer_stroke = cv2.subtract(dilated, mask_np)
                
                # --- 修复 2：边缘修正逻辑升级 (解决边缘描边断开问题) ---
                # 之前用 cv2.rectangle 可能有坐标误差，现在直接用 numpy 切片强制指定边缘区域
                border_mask = np.zeros((h, w), dtype=np.uint8)
                t = 描边宽度 + 2  # 多给2像素冗余，防止刚好卡在边界线
                
                # 将图像四周的边缘区域全部设为 255 (白色)
                border_mask[:t, :] = 255       # 上边缘
                border_mask[-t:, :] = 255      # 下边缘
                border_mask[:, :t] = 255       # 左边缘
                border_mask[:, -t:] = 255      # 右边缘
                
                # 计算内描边 (Original - Erode)
                # 强制指定 borderType=cv2.BORDER_CONSTANT，确保边缘外的像素被视为黑色(0)，从而触发腐蚀
                eroded = cv2.erode(mask_np, kernel, iterations=1, borderType=cv2.BORDER_CONSTANT, borderValue=0)
                inner_stroke = cv2.subtract(mask_np, eroded)
                
                # 组合逻辑：正常区域显示外描边，边缘区域(border_mask)显示内描边
                # bitwise_and 确保内描边只在边缘生效，不会影响图像中间
                stroke_mask = cv2.bitwise_or(outer_stroke, cv2.bitwise_and(inner_stroke, border_mask))
                
                draw_layer[stroke_mask > 0] = color
                alpha_layer[stroke_mask > 0] = 描边不透明度

            # 合成
            img_float = img_np.astype(np.float32) / 255.0
            draw_float = draw_layer.astype(np.float32) / 255.0
            alpha_expanded = alpha_layer[..., np.newaxis]
            
            blended = draw_float * alpha_expanded + img_float * (1.0 - alpha_expanded)
            blended = np.clip(blended, 0.0, 1.0)
            
            result_images.append(torch.from_numpy(blended))

        return (torch.stack(result_images),)