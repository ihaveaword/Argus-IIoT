# 🤝 团队协作指南

## 首次克隆项目

```bash
# 1. 克隆仓库
git clone <仓库地址>
cd Argus-IIoT

# 2. 后端环境
cd backend
cp .env.example .env          # 复制环境变量
python3 -m venv venv          # 创建虚拟环境
source venv/bin/activate      # 激活（Mac/Linux）
# venv\Scripts\activate       # 激活（Windows）
pip install -r requirements.txt
cd ..

# 3. 前端环境
cd frontend
npm install
cd ..
```

---

## 日常开发流程

### 1️⃣ 开始工作前

```bash
git pull origin main          # 拉取最新代码
```

> ⚠️ 如果提示冲突，先解决冲突再继续

### 2️⃣ 开发中

```bash
# 后端开发
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 前端开发（新终端）
cd frontend
npm run dev
```

### 3️⃣ 提交代码

```bash
git add .
git commit -m "描述你做了什么"
git push origin main
```

---

## ⚠️ 注意事项

### 不要提交的文件（已配置在 .gitignore）
- ❌ `backend/venv/` - 虚拟环境
- ❌ `frontend/node_modules/` - 前端依赖
- ❌ `backend/models/*.pt` - 模型文件（太大）
- ❌ `backend/uploads/` 和 `backend/outputs/` - 临时文件
- ❌ `backend/.env` - 环境变量（含敏感信息）

### 要提交的文件
- ✅ 所有 `.py`、`.vue`、`.js` 源代码
- ✅ `requirements.txt`、`package.json` 配置文件
- ✅ `README.md`、文档

---

## 🆘 常见问题

### Q: `git pull` 提示冲突怎么办？
```bash
# 查看冲突文件
git status

# 手动编辑冲突文件，删除 <<<<<<< ======= >>>>>>> 标记
# 然后：
git add .
git commit -m "解决冲突"
git push
```

### Q: 后端报错 `ModuleNotFoundError`？
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Q: 前端报错 `Cannot find module`？
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📞 遇到问题？

联系项目负责人或在团队群里提问。
