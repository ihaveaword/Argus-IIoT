"""
FastAPI 目标检测服务 - 主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routes import router
from app.core.config import settings

# 创建 FastAPI 应用
app = FastAPI(
    title="Argus-IIoT API",
    description="轻量级边缘云协同目标检测系统 - 基于 YOLOv8 的全天候智能感知服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS（跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vue 开发服务器
        "http://localhost:3000",  # 备用端口
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保目录存在
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# 挂载静态文件目录（用于访问输出结果）
app.mount("/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")

# 注册路由
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Argus-IIoT API 服务",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
