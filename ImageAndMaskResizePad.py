import torch
import numpy as np
from PIL import Image

class ImageAndMaskResizePad:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "reference_image": ("IMAGE",),
                "reference_mask": ("MASK",),
                "target_image": ("IMAGE",),
                "alignment": (["center", "top_center", "bottom_center", "left_center", "right_center", "top_left", "top_right", "bottom_left", "bottom_right"], {"default": "center"}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "execute"
    CATEGORY = "ImageProcessing/Resize"

    def _tensor_to_pil(self, tensor):
        # Converts a torch tensor (B, H, W, C) or (B, H, W) to a single PIL Image
        image_np = tensor[0].cpu().numpy()
        image_np = (image_np * 255).astype(np.uint8)
        
        if image_np.ndim == 2: # Mask
            return Image.fromarray(image_np, mode='L')
        else: # Image
            return Image.fromarray(image_np, mode='RGB')

    def _pil_to_tensor(self, pil_image):
        # Converts a PIL Image to a torch tensor (1, H, W, C) or (1, H, W)
        image_np = np.array(pil_image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(image_np)
        
        if tensor.ndim == 2: # Mask
            return tensor.unsqueeze(0)
        else: # Image
             return tensor.unsqueeze(0)


    def execute(self, reference_image, reference_mask, target_image, alignment):
        # Convert input tensors to PIL images for processing
        ref_img_pil = self._tensor_to_pil(reference_image)
        ref_mask_pil = self._tensor_to_pil(reference_mask)
        
        # Get target dimensions from the target_image tensor
        target_height, target_width = target_image.shape[1], target_image.shape[2]
        
        # --- Resizing Logic ---
        ref_width, ref_height = ref_img_pil.size
        target_shortest_side = min(target_width, target_height)
        
        if max(ref_width, ref_height) == 0:
            scale_factor = 0
        else:
            scale_factor = target_shortest_side / max(ref_width, ref_height)
            
        new_width = int(ref_width * scale_factor)
        new_height = int(ref_height * scale_factor)
        
        # Handle cases where the input image is tiny or empty
        if new_width < 1 or new_height < 1:
            padded_img = Image.new('RGB', (target_width, target_height), (0, 0, 0))
            padded_mask = Image.new('L', (target_width, target_height), 0)
        else:
            resized_img = ref_img_pil.resize((new_width, new_height), Image.LANCZOS)
            resized_mask = ref_mask_pil.resize((new_width, new_height), Image.NEAREST)

            # --- Padding Logic ---
            padded_img = self.pad_image(resized_img, target_width, target_height, alignment, fill_color=(0, 0, 0))
            padded_mask = self.pad_image(resized_mask, target_width, target_height, alignment, fill_color=0)

        # --- Convert back to Tensors ---
        output_image = self._pil_to_tensor(padded_img)
        output_mask = self._pil_to_tensor(padded_mask)
        
        return (output_image, output_mask)

    def pad_image(self, image, target_width, target_height, alignment, fill_color):
        # Create a new background image
        new_img = Image.new(image.mode, (target_width, target_height), fill_color)

        original_width, original_height = image.size
        
        # Calculate position
        if 'left' in alignment:
            x_pos = 0
        elif 'right' in alignment:
            x_pos = target_width - original_width
        else: # center
            x_pos = (target_width - original_width) // 2

        if 'top' in alignment:
            y_pos = 0
        elif 'bottom' in alignment:
            y_pos = target_height - original_height
        else: # center
            y_pos = (target_height - original_height) // 2
            
        # Paste the resized image onto the background
        new_img.paste(image, (x_pos, y_pos))
        return new_img

NODE_CLASS_MAPPINGS = {
    "ImageAndMaskResizePad": ImageAndMaskResizePad
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageAndMaskResizePad": "Image and Mask Resize Pad"
}