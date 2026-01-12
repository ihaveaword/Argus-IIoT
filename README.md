# 🎯 Argus-IIoT

> **"Argus Panoptes, the All-Seeing Guardian"**  
> *Argus Panoptes* 是希腊神话中的"百眼巨人"，拥有一百只眼睛，哪怕在睡觉时也有眼睛睁着，是完美的监视者。**Argus-IIoT** 代表全天候、无死角的智能感知能力，象征系统对边缘侧数据的极致掌控。

## 项目简介

基于 **FastAPI + Vue 3** 的前后端分离架构，使用 YOLOv8 进行目标检测的轻量级边缘云协同系统。

## 📁 项目结构

```
Argus-IIoT/
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

## 🤝 团队协作

> 📖 **详细协作指南**: 查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 🚀 快速开始

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

### 快速启动后端

```bash
cd backend
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

### 快速启动前端
```bash
cd frontend
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