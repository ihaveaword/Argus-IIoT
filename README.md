# 🎯 Argus-IIoT 平台

**FastAPI + Vue 3** 前后端分离架构，集成 **YOLOv8 目标检测** 和 **微服务架构审计工具**。

## ✨ 功能特性

### 1. 目标检测 (Object Detection)
- 基于 YOLOv8 的图片和视频目标检测
- 实时推理和结果可视化
- 支持多种图片和视频格式

### 2. 架构审计 (Architecture Audit) 🆕
- **架构模式识别**: 自动检测 MVC、Hexagonal、Clean Architecture、DDD 等模式
- **API 契约分析**: 分析 REST/gRPC/GraphQL API，生成一致性报告
- **技术栈审计**: 审查数据库、消息队列、缓存等技术选型
- **交互式报告**: 生成 HTML 报告，包含代码跳转链接和架构图
- **ADR 模板**: 统一架构决策记录规范

详细文档: [ARCHITECTURE_AUDIT.md](./ARCHITECTURE_AUDIT.md)

## 📁 项目结构

```
object-detection-dashboard/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # 入口文件
│   │   ├── api/routes.py    # API 路由
│   │   ├── core/config.py   # 配置
│   │   ├── services/detector.py  # 检测服务
│   │   └── utils/visualization.py
│   ├── models/              # 模型权重
│   ├── requirements.txt
│   └── .env
│
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── assets/main.css
│   │   ├── services/api.js
│   │   └── views/
│   │       ├── HomeView.vue
│   │       ├── ImageDetection.vue
│   │       └── VideoDetection.vue
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## � 团队协作设置

### 首次克隆项目后的设置步骤

```bash
# 1. 克隆仓库
git clone <your-repo-url>
cd Argus-IIoT

# 2. 后端环境配置
cd backend

# 复制环境变量模板
cp .env.example .env

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 下载 YOLOv8 模型（首次运行会自动下载）
# 或手动下载：wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

cd ..

# 3. 前端环境配置
cd frontend
npm install
cd ..
```

### ⚠️ 重要提醒
- ✅ **不要提交**：虚拟环境 (`venv/`)、依赖包 (`node_modules/`)、模型文件 (`*.pt`)
- ✅ **不要提交**：上传/输出目录 (`uploads/`, `outputs/`)、环境变量文件 (`.env`)
- ✅ **要提交**：源代码、配置文件、README、.gitignore

## �🚀 快速开始

### 1. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn app.main:app --reload --port 8000
```

后端 API 文档: http://localhost:8000/docs

### 2. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

前端页面: http://localhost:5173

## 📡 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/models` | 获取模型列表 |
| POST | `/api/detect/image` | 图片检测 |
| POST | `/api/detect/video` | 视频检测 |

## 🖥️ 技术栈

- **后端**: FastAPI, YOLOv8, OpenCV, PyTorch
- **前端**: Vue 3, Vite, Axios, Vue Router
- **部署**: Docker (可选)

## 📝 开发说明

- 后端运行在 8000 端口
- 前端开发服务器运行在 5173 端口
- Vite 已配置代理，自动将 `/api` 请求转发到后端