from .ImageAndMaskResizePad import NODE_CLASS_MAPPINGS as IM_Resize_Mappings, NODE_DISPLAY_NAME_MAPPINGS as IM_Resize_Display_Mappings
from .SeamlessTiling import NODE_CLASS_MAPPINGS as ST_Tiling_Mappings, NODE_DISPLAY_NAME_MAPPINGS as ST_Tiling_Display_Mappings
# 导入新节点
from .ImageMaskingProcessor import Onion_ImageMaskingProcessor

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# 更新旧节点
NODE_CLASS_MAPPINGS.update(IM_Resize_Mappings)
NODE_CLASS_MAPPINGS.update(ST_Tiling_Mappings)
NODE_DISPLAY_NAME_MAPPINGS.update(IM_Resize_Display_Mappings)
NODE_DISPLAY_NAME_MAPPINGS.update(ST_Tiling_Display_Mappings)

# 注册新节点
NODE_CLASS_MAPPINGS["Onion_ImageMaskingProcessor"] = Onion_ImageMaskingProcessor
NODE_DISPLAY_NAME_MAPPINGS["Onion_ImageMaskingProcessor"] = "ImageMaskingProcessor"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print("✅ Loaded Custom Nodes: ImageAndMaskResizePad, SeamlessTiling, ImageMaskingProcessor")