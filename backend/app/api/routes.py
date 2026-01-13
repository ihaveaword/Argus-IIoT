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
from app.architecture.audit_service import ArchitectureAuditService
from app.architecture.models.architecture_models import ArchitectureAuditReport
from fastapi.responses import HTMLResponse, Response

router = APIRouter()

# Initialize architecture audit service
audit_service = None


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


# ============ Architecture Audit Endpoints ============

@router.post("/architecture/audit")
async def audit_architecture(
    repo_urls: List[str] = Form(None),
    local_paths: List[str] = Form(None)
):
    """
    执行架构一致性审计
    
    - **repo_urls**: GitHub仓库URL列表
    - **local_paths**: 本地仓库路径列表
    """
    global audit_service
    
    if not repo_urls and not local_paths:
        raise HTTPException(
            status_code=400,
            detail="必须提供至少一个仓库URL或本地路径"
        )
    
    try:
        # Initialize audit service if not already done
        if audit_service is None:
            audit_service = ArchitectureAuditService()
        
        # Perform audit
        report = audit_service.audit_repositories(
            repo_urls=repo_urls or [],
            local_paths=local_paths or []
        )
        
        return {
            "success": True,
            "report_id": report.timestamp.replace(" ", "_").replace(":", "-"),
            "summary": {
                "total_repositories": report.total_repositories,
                "total_services": report.total_services,
                "total_endpoints": report.api_report.total_endpoints,
                "circular_dependencies": len(report.topology.circular_dependencies),
                "bottlenecks": len(report.topology.bottlenecks),
                "breaking_changes": len(report.api_report.breaking_changes)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"审计失败: {str(e)}")


@router.get("/architecture/report/{report_id}", response_class=HTMLResponse)
async def get_architecture_report(report_id: str):
    """
    获取架构审计HTML报告
    """
    # In a real implementation, you would load the report from storage
    # For now, return a message
    return """
    <html>
        <body>
            <h1>架构审计报告</h1>
            <p>报告ID: {}</p>
            <p>请先执行审计以生成报告</p>
        </body>
    </html>
    """.format(report_id)


@router.post("/architecture/analyze-local")
async def analyze_local_repository():
    """
    分析当前本地仓库（用于演示）
    """
    global audit_service
    
    try:
        # Initialize audit service if not already done
        if audit_service is None:
            audit_service = ArchitectureAuditService()
        
        # Analyze the current repository
        current_repo_path = "/home/runner/work/Argus-IIoT/Argus-IIoT"
        
        report = audit_service.audit_repositories(
            repo_urls=[],
            local_paths=[current_repo_path]
        )
        
        # Generate HTML report
        html_report = audit_service.generate_html_report(report)
        
        # Save report to outputs directory
        report_filename = f"architecture_report_{report.timestamp.replace(' ', '_').replace(':', '-')}.html"
        report_path = Path(settings.OUTPUT_DIR) / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # Generate SVG diagrams
        topology_svg = audit_service.generate_topology_svg(report.topology)
        topology_filename = f"topology_{report.timestamp.replace(' ', '_').replace(':', '-')}.svg"
        topology_path = Path(settings.OUTPUT_DIR) / topology_filename
        
        with open(topology_path, 'w', encoding='utf-8') as f:
            f.write(topology_svg)
        
        pattern_svg = audit_service.generate_pattern_distribution_svg(report)
        pattern_filename = f"patterns_{report.timestamp.replace(' ', '_').replace(':', '-')}.svg"
        pattern_path = Path(settings.OUTPUT_DIR) / pattern_filename
        
        with open(pattern_path, 'w', encoding='utf-8') as f:
            f.write(pattern_svg)
        
        return {
            "success": True,
            "report": {
                "html_url": f"/outputs/{report_filename}",
                "topology_svg_url": f"/outputs/{topology_filename}",
                "patterns_svg_url": f"/outputs/{pattern_filename}"
            },
            "summary": {
                "total_repositories": report.total_repositories,
                "total_services": report.total_services,
                "total_endpoints": report.api_report.total_endpoints,
                "circular_dependencies": len(report.topology.circular_dependencies),
                "bottlenecks": len(report.topology.bottlenecks),
                "breaking_changes": len(report.api_report.breaking_changes),
                "tech_stack_items": len(report.tech_stack_report.tech_items),
                "version_conflicts": len(report.tech_stack_report.version_conflicts)
            },
            "details": {
                "repositories": [
                    {
                        "name": repo.repo_name,
                        "patterns": [p.value if hasattr(p, 'value') else str(p) for p in repo.architecture_patterns],
                        "services": repo.services,
                        "api_endpoints": len(repo.api_endpoints),
                        "tech_stack": len(repo.tech_stack)
                    }
                    for repo in report.repositories
                ]
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


from typing import List
