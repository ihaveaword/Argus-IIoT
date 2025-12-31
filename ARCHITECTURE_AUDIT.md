# Architecture Audit Tool

## 概述

全面的微服务架构审计工具，可以扫描代码库并生成详细的架构分析报告。

## 功能特性

### 1. 架构模式识别 🏛️
自动检测常见的架构模式：
- **MVC** (Model-View-Controller)
- **Clean Architecture** (清洁架构)
- **Hexagonal Architecture** (六边形架构)
- **DDD** (Domain-Driven Design)
- **Layered Architecture** (分层架构)
- **Microservices** (微服务架构)

### 2. API 契约分析 🔌
- 支持 REST API (FastAPI, Flask, Django, Express, NestJS)
- 支持 GraphQL schema 检测
- 支持 gRPC proto 文件检测
- 生成 API 契约一致性报告
- 识别命名不一致和潜在的兼容性问题

### 3. 技术栈审计 🛠️
扫描并分析：
- **数据库**: PostgreSQL, MySQL, MongoDB, Redis, SQLite, Cassandra, Elasticsearch, DynamoDB
- **消息队列**: RabbitMQ, Kafka, Redis Pub/Sub, AWS SQS, Google Pub/Sub, NATS
- **缓存**: Redis, Memcached, Varnish, CDN
- **Web 框架**: FastAPI, Flask, Django, Express, NestJS, Spring Boot, Gin, Echo
- **容器化**: Docker, Docker Compose, Kubernetes
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins, CircleCI

### 4. 交互式 HTML 报告 📊
生成完整的 HTML 报告，包含：
- 架构模式可视化
- API 端点列表和统计
- 技术栈对比
- 标准化建议
- 可下载的 ADR 模板

### 5. ADR 模板 📝
提供标准化的架构决策记录 (Architecture Decision Records) 模板，用于统一技术文档规范。

## API 端点

### 扫描单个仓库
```http
POST /api/audit/scan
Content-Type: application/json

{
  "directory_path": "/path/to/repository"
}
```

**响应示例**:
```json
{
  "success": true,
  "audit_id": "20231231_123456",
  "directory": "/path/to/repository",
  "timestamp": "2023-12-31T12:34:56",
  "summary": {
    "architecture_patterns": 3,
    "api_endpoints": 15,
    "tech_stack_items": 8
  }
}
```

### 获取审计结果
```http
GET /api/audit/audit/{audit_id}
```

### 查看 HTML 报告
```http
GET /api/audit/report/{audit_id}
```
在浏览器中打开此 URL 可查看交互式 HTML 报告。

### 列出所有审计
```http
GET /api/audit/audits
```

### 扫描多个仓库
```http
POST /api/audit/scan-multiple
Content-Type: application/json

{
  "directories": [
    "/path/to/repo1",
    "/path/to/repo2",
    "/path/to/repo3"
  ]
}
```

## 使用示例

### Python 示例
```python
import requests

# 扫描仓库
response = requests.post('http://localhost:8000/api/audit/scan', json={
    'directory_path': '/home/user/my-project'
})

result = response.json()
audit_id = result['audit_id']

print(f"扫描完成! Audit ID: {audit_id}")
print(f"发现架构模式: {result['summary']['architecture_patterns']}")
print(f"API 端点数量: {result['summary']['api_endpoints']}")

# 在浏览器中查看报告
report_url = f"http://localhost:8000/api/audit/report/{audit_id}"
print(f"查看报告: {report_url}")
```

### cURL 示例
```bash
# 扫描仓库
curl -X POST http://localhost:8000/api/audit/scan \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/home/user/my-project"}'

# 获取审计结果
curl http://localhost:8000/api/audit/audit/20231231_123456

# 列出所有审计
curl http://localhost:8000/api/audit/audits
```

### 前端使用
在浏览器中访问 `http://localhost:5173/audit` 使用图形化界面进行架构审计。

## 架构分析示例

### 检测到的模式
```json
{
  "name": "Layered",
  "confidence": 0.8,
  "indicators": [
    "Directory: backend/app/api",
    "Directory: backend/app/services",
    "Directory: backend/app/core"
  ],
  "evidence": [
    "app/api/routes.py",
    "app/services/detector.py",
    "app/services/audit_service.py"
  ]
}
```

### API 端点分析
```json
{
  "type": "REST",
  "framework": "FastAPI",
  "endpoints": [
    {
      "path": "/api/health",
      "method": "GET",
      "handler": "health_check",
      "file": "app/api/routes.py",
      "line": 22
    },
    {
      "path": "/api/audit/scan",
      "method": "POST",
      "handler": "scan_repository",
      "file": "app/api/audit_routes.py",
      "line": 24
    }
  ]
}
```

### 技术栈报告
```json
{
  "databases": ["Redis"],
  "message_queues": [],
  "caches": ["Redis"],
  "web_frameworks": ["FastAPI"],
  "languages": {
    "Python": 1,
    "JavaScript/TypeScript": 1
  },
  "containerization": ["Docker"],
  "ci_cd": ["GitHub Actions"]
}
```

## 标准化建议

工具会自动生成标准化建议，例如：
- 数据库技术过多时建议整合
- 缺少缓存层时建议添加
- 缺少 CI/CD 时建议实施
- API 命名不一致时建议统一

## ADR 模板

工具提供可下载的 ADR 模板，包含以下部分：
- 状态 (Status)
- 上下文 (Context)
- 决策 (Decision)
- 后果 (Consequences)
- 替代方案 (Alternatives Considered)
- 参考 (References)

## 技术实现

### 后端模块
- `architecture_analyzer.py`: 架构模式检测
- `api_analyzer.py`: API 契约分析
- `tech_stack_auditor.py`: 技术栈审计
- `report_generator.py`: HTML 报告生成
- `audit_service.py`: 审计服务编排

### 分析算法
- 使用 AST (抽象语法树) 解析 Python 代码
- 正则表达式匹配 API 路由模式
- 目录结构分析识别架构模式
- 依赖文件扫描 (requirements.txt, package.json, go.mod)

## 扩展性

工具设计为可扩展：
- 添加新的架构模式检测规则
- 支持更多编程语言和框架
- 自定义报告模板
- 集成更多分析工具 (如 CodeQL, SonarQube)

## 限制

- 目前主要支持 Python 和 JavaScript/TypeScript 项目
- 需要访问文件系统来扫描代码
- 不执行代码，仅进行静态分析
- 对于加密或混淆的代码可能无法准确分析

## 未来计划

- [ ] 支持更多编程语言 (Go, Java, C#, Ruby)
- [ ] 生成系统调用拓扑图 (SVG)
- [ ] 检测循环依赖
- [ ] 性能瓶颈分析
- [ ] 集成代码质量指标
- [ ] 支持 Git 历史分析
- [ ] 生成架构演进报告
