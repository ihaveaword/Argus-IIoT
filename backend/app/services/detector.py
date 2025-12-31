"""
YOLOv8 目标检测服务
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from ultralytics import YOLO
import torch

from app.core.config import settings


class DetectorService:
    """目标检测服务类"""
    
    _instance: Optional["DetectorService"] = None
    _model: Optional[YOLO] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._load_model()
    
    def _load_model(self, model_name: str = None):
        """加载模型"""
        model_path = model_name or settings.MODEL_PATH
        
        # 检查模型文件是否存在
        if not Path(model_path).exists():
            # 如果不存在，使用默认模型名（会自动下载）
            model_path = "yolov8n.pt"
        
        self._model = YOLO(model_path)
        
        # 获取设备信息
        self.device = "mps" if torch.backends.mps.is_available() else \
                      "cuda" if torch.cuda.is_available() else "cpu"
        print(f"✅ 模型已加载: {model_path}, 设备: {self.device}")
    
    def detect_image(
        self, 
        image: np.ndarray, 
        confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        对图片进行目标检测
        
        Args:
            image: 输入图片 (BGR 格式)
            confidence: 置信度阈值
            
        Returns:
            检测结果字典
        """
        # 执行推理
        results = self._model.predict(image, conf=confidence, verbose=False)
        
        # 解析结果
        detections = []
        if results[0].boxes is not None:
            for box in results[0].boxes:
                conf = float(box.conf[0])
                if conf >= confidence:
                    cls_id = int(box.cls[0])
                    class_name = results[0].names[cls_id]
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    detections.append({
                        "class": class_name,
                        "confidence": round(conf, 4),
                        "bbox": [x1, y1, x2, y2]
                    })
        
        # 绘制标注图
        annotated_image = self._draw_detections(image, detections)
        
        return {
            "detections": detections,
            "annotated_image": annotated_image,
            "total_objects": len(detections)
        }
    
    def _draw_detections(
        self, 
        image: np.ndarray, 
        detections: List[Dict]
    ) -> np.ndarray:
        """在图像上绘制检测结果"""
        annotated = image.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            class_name = det["class"]
            conf = det["confidence"]
            
            # 绘制矩形框（绿色）
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 绘制标签背景
            label = f"{class_name} {conf:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(
                annotated,
                (x1, y1 - label_size[1] - 4),
                (x1 + label_size[0], y1),
                (0, 255, 0),
                -1
            )
            
            # 绘制文字
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                1
            )
        
        return annotated
    
    def detect_video(
        self,
        video_path: str,
        output_path: str,
        confidence: float = 0.5,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        对视频进行目标检测
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            confidence: 置信度阈值
            progress_callback: 进度回调函数
            
        Returns:
            处理结果字典
        """
        cap = cv2.VideoCapture(video_path)
        
        # 获取视频参数
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        total_detections = 0
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 推理
            result = self.detect_image(frame, confidence)
            total_detections += result["total_objects"]
            
            # 写入处理后的帧
            out.write(result["annotated_image"])
            
            frame_idx += 1
            
            # 回调进度
            if progress_callback:
                progress_callback(frame_idx, frame_count)
        
        cap.release()
        out.release()
        
        return {
            "total_frames": frame_count,
            "fps": fps,
            "resolution": f"{width}x{height}",
            "total_detections": total_detections,
            "output_path": output_path
        }


# 全局单例
detector_service = DetectorService()
