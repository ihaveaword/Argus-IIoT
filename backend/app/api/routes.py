"""
API 路由定义
"""

import os
import uuid
import time
import cv2
import numpy as np
import aiofiles
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.detector import detector_service
from app.utils.visualization import encode_image_to_base64

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "目标检测 API",
        "device": detector_service.device
    }


@router.get("/models")
async def get_models():
    """获取可用模型列表"""
    models_dir = Path(settings.MODELS_DIR)
    models = []
    
    if models_dir.exists():
        for f in models_dir.glob("*.pt"):
            models.append(f.name)
    
    # 默认模型
    if not models:
        models = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt"]
    
    return {"models": models}


@router.post("/detect/image")
async def detect_image(
    file: UploadFile = File(...),
    confidence: float = Form(default=0.5)
):
    """
    图片目标检测
    
    - **file**: 上传的图片文件
    - **confidence**: 置信度阈值 (0-1)
    """
    # 验证文件类型
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的图片格式: {file.content_type}"
        )
    
    # 读取图片
    contents = await file.read()
    
    # 检查文件大小
    if len(contents) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"图片太大，最大允许 {settings.MAX_IMAGE_SIZE // 1024 // 1024}MB"
        )
    
    # 解码图片
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="无法解码图片")
    
    # 开始计时
    start_time = time.time()
    
    # 执行检测
    result = detector_service.detect_image(image, confidence)
    
    # 计算推理时间
    inference_time = time.time() - start_time
    
    # 编码标注图为 Base64
    annotated_base64 = encode_image_to_base64(result["annotated_image"])
    
    return JSONResponse({
        "success": True,
        "detections": result["detections"],
        "annotated_image": annotated_base64,
        "stats": {
            "total_objects": result["total_objects"],
            "inference_time": round(inference_time, 4),
            "image_size": f"{image.shape[1]}x{image.shape[0]}"
        }
    })


@router.post("/detect/video")
async def detect_video(
    file: UploadFile = File(...),
    confidence: float = Form(default=0.5)
):
    """
    视频目标检测
    
    - **file**: 上传的视频文件
    - **confidence**: 置信度阈值 (0-1)
    """
    # 验证文件类型
    if file.content_type not in settings.ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的视频格式: {file.content_type}"
        )
    
    # 生成唯一文件名
    task_id = str(uuid.uuid4())[:8]
    input_filename = f"{task_id}_input.mp4"
    output_filename = f"{task_id}_output.mp4"
    
    input_path = Path(settings.UPLOAD_DIR) / input_filename
    output_path = Path(settings.OUTPUT_DIR) / output_filename
    
    # 保存上传的视频
    contents = await file.read()
    
    # 检查文件大小
    if len(contents) > settings.MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"视频太大，最大允许 {settings.MAX_VIDEO_SIZE // 1024 // 1024}MB"
        )
    
    async with aiofiles.open(input_path, 'wb') as f:
        await f.write(contents)
    
    # 开始计时
    start_time = time.time()
    
    # 执行视频检测
    try:
        result = detector_service.detect_video(
            str(input_path),
            str(output_path),
            confidence
        )
    except Exception as e:
        # 清理临时文件
        if input_path.exists():
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=f"视频处理失败: {str(e)}")
    
    # 计算处理时间
    processing_time = time.time() - start_time
    
    # 清理输入文件
    if input_path.exists():
        os.remove(input_path)
    
    return JSONResponse({
        "success": True,
        "task_id": task_id,
        "stats": {
            "total_frames": result["total_frames"],
            "fps": result["fps"],
            "resolution": result["resolution"],
            "total_detections": result["total_detections"],
            "processing_time": round(processing_time, 2)
        },
        "output_url": f"/outputs/{output_filename}"
    })


@router.get("/result/{task_id}")
async def get_result(task_id: str):
    """获取处理结果"""
    output_filename = f"{task_id}_output.mp4"
    output_path = Path(settings.OUTPUT_DIR) / output_filename
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="结果不存在或已过期")
    
    return {
        "task_id": task_id,
        "status": "completed",
        "output_url": f"/outputs/{output_filename}"
    }
