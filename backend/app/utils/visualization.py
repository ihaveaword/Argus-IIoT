"""
可视化工具函数
"""

import cv2
import base64
import numpy as np
from typing import Tuple


def encode_image_to_base64(image: np.ndarray) -> str:
    """
    将图像编码为 Base64 字符串
    
    Args:
        image: BGR 格式的图像数组
        
    Returns:
        Base64 编码的字符串
    """
    # 编码为 JPEG
    _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    
    # 转换为 Base64
    base64_str = base64.b64encode(buffer).decode('utf-8')
    
    return f"data:image/jpeg;base64,{base64_str}"


def decode_base64_to_image(base64_str: str) -> np.ndarray:
    """
    将 Base64 字符串解码为图像
    
    Args:
        base64_str: Base64 编码的图像字符串
        
    Returns:
        BGR 格式的图像数组
    """
    # 移除 data URL 前缀
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    
    # 解码
    img_data = base64.b64decode(base64_str)
    img_array = np.frombuffer(img_data, dtype=np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    return image


def resize_image(
    image: np.ndarray, 
    max_size: Tuple[int, int] = (1920, 1080)
) -> np.ndarray:
    """
    按比例缩放图像
    
    Args:
        image: 输入图像
        max_size: 最大尺寸 (宽, 高)
        
    Returns:
        缩放后的图像
    """
    h, w = image.shape[:2]
    max_w, max_h = max_size
    
    # 计算缩放比例
    scale = min(max_w / w, max_h / h)
    
    if scale < 1:
        new_w = int(w * scale)
        new_h = int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    return image
