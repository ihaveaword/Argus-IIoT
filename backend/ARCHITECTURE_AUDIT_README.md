# 架构一致性审计系统

## 📖 概述

本系统提供全面的微服务架构分析和审计功能，能够自动扫描代码仓库，识别架构模式，分析API契约，绘制服务拓扑图，并提供技术栈标准化建议。

## ✨ 功能特性

### 1. 🏛️ 架构模式识别
自动检测和识别多种架构模式：
- MVC (Model-View-Controller)
- Hexagonal Architecture (六边形架构)
- Clean Architecture (简洁架构)
- Domain-Driven Design (领域驱动设计)
- Layered Architecture (分层架构)
- Event-Driven Architecture (事件驱动架构)

**工作原理：**
- 分析目录结构和文件命名
- 扫描代码中的架构关键字和模式
- 计算每种模式的置信度评分

### 2. 🔌 API契约分析
分析所有API接口并生成一致性报告：
- 支持 REST、gRPC、GraphQL 协议
- 自动提取API端点定义
- 检测破坏性变更
- 标注API标准违规

**检测范围：**
- REST: FastAPI, Flask, Spring, Express 等框架
- gRPC: Proto文件和服务定义
- GraphQL: Schema定义和查询/变更

### 3. 🕸️ 服务拓扑图
绘制完整的系统调用拓扑：
- 识别同步和异步调用
- 检测循环依赖
- 标注性能瓶颈
- 生成可交互的SVG图表

**拓扑分析：**
- HTTP/HTTPS 调用检测
- 消息队列（RabbitMQ, Kafka）通信
- gRPC 服务调用
- 高流量服务识别

### 4. 🛠️ 技术栈审计
全面审查技术选型：
- 数据库 (PostgreSQL, MySQL, MongoDB, Redis等)
- 消息队列 (RabbitMQ, Kafka, NATS等)
- 缓存 (Redis, Memcached等)
- Web框架 (FastAPI, Express, Spring Boot等)
- 编程语言

**分析输出：**
- 版本冲突检测
- 标准化建议
- 技术栈分布统计

### 5. 📝 ADR模板
提供架构决策记录（Architecture Decision Records）模板，统一技术文档规范。

### 6. 📊 交互式HTML报告
生成美观的HTML报告，包含：
- 可切换的多标签视图
- 统计数据可视化
- 代码位置链接
- SVG架构图表
- 响应式设计

## 🚀 快速开始

### 使用Web界面

1. 启动后端服务：
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. 启动前端服务：
```bash
cd frontend
npm run dev
```

3. 访问 `http://localhost:5173/architecture`

4. 点击"分析本地仓库"按钮

5. 查看生成的报告

### 使用API

```bash
# 分析当前仓库
curl -X POST http://localhost:8000/api/architecture/analyze-local
```

### 使用测试脚本

```bash
cd backend
python test_architecture_audit.py
```

## 📁 项目结构

```
backend/app/architecture/
├── __init__.py
├── audit_service.py              # 主要审计服务
├── models/
│   ├── __init__.py
│   └── architecture_models.py    # 数据模型定义
├── analyzers/
│   ├── __init__.py
│   ├── pattern_detector.py       # 架构模式检测器
│   ├── api_analyzer.py           # API分析器
│   ├── topology_analyzer.py      # 拓扑分析器
│   └── tech_stack_analyzer.py    # 技术栈分析器
├── generators/
│   ├── __init__.py
│   ├── html_report_generator.py  # HTML报告生成器
│   └── svg_diagram_generator.py  # SVG图表生成器
└── utils/
    ├── __init__.py
    └── github_scanner.py         # GitHub仓库扫描器
```

## 🔍 技术实现

### 架构模式检测
- **目录结构分析**：检查特定目录名称（如 models, views, controllers）
- **文件命名模式**：识别特定文件命名约定
- **代码关键字扫描**：搜索架构特定的类名和注解
- **置信度评分**：综合多个指标计算置信度

### API提取
使用正则表达式匹配常见的API定义模式：
- FastAPI: `@app.get("/path")`
- Spring: `@GetMapping("/path")`
- Express: `router.get("/path")`
- gRPC: `rpc MethodName (Request) returns (Response)`
- GraphQL: `type Query { field: Type }`

### 拓扑构建
- **依赖关系提取**：分析HTTP调用、gRPC调用、消息队列订阅
- **图形分析**：使用深度优先搜索检测循环依赖
- **瓶颈识别**：统计入度和出度，识别高流量节点

### SVG生成
- 使用圆形布局算法排列服务节点
- 根据依赖类型（同步/异步）使用不同颜色
- 突出显示问题节点（循环依赖、性能瓶颈）

## 🎯 使用场景

1. **微服务迁移**：评估现有系统架构，规划迁移路径
2. **代码审查**：快速了解新项目的架构设计
3. **技术债务评估**：识别架构不一致和技术选型问题
4. **文档生成**：自动生成架构文档和决策记录
5. **标准化推进**：统一多个团队的技术栈和架构风格

## ⚙️ 配置选项

### 模式检测阈值
可以在 `pattern_detector.py` 中调整置信度阈值：
```python
if score >= 0.3:  # 默认阈值为0.3
    detected_patterns.append(pattern)
```

### 瓶颈检测阈值
在 `topology_analyzer.py` 中调整：
```python
if count >= 5:  # 入度>=5视为潜在瓶颈
    bottlenecks.append(...)
```

## 🔮 未来增强

- [ ] 支持更多架构模式（CQRS, Event Sourcing等）
- [ ] 增加代码质量指标分析
- [ ] 支持实时监控和告警
- [ ] 集成CI/CD流程
- [ ] 支持多仓库批量分析
- [ ] 机器学习优化模式识别
- [ ] 生成Markdown格式报告
- [ ] 支持自定义分析规则

## 📝 ADR模板使用指南

### 创建ADR文档
1. 在仓库中创建 `docs/adr/` 目录
2. 使用递增编号命名：`ADR-0001-标题.md`
3. 使用提供的模板填写内容

### ADR最佳实践
- 记录所有重要的架构决策
- 包含决策背景和考虑的备选方案
- 说明决策的后果和风险
- ADR一旦创建不应修改，而应创建新的ADR替代
- 定期回顾和更新ADR状态

## 🤝 贡献

欢迎贡献代码和建议！请参考项目的贡献指南。

## 📄 许可证

本项目采用 MIT 许可证。
