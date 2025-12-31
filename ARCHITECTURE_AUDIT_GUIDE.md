# Architecture Audit Quick Start Guide

## What was implemented

A comprehensive architecture consistency audit system that analyzes microservice repositories and generates detailed reports including:

1. **Architecture Pattern Detection** - Identifies MVC, Hexagonal, Clean Architecture, DDD, etc.
2. **API Contract Analysis** - Analyzes REST/gRPC/GraphQL endpoints and detects breaking changes
3. **Service Topology** - Maps service dependencies and identifies circular dependencies and bottlenecks
4. **Tech Stack Audit** - Reviews databases, message queues, caches, and provides standardization recommendations
5. **ADR Templates** - Provides Architecture Decision Record templates for documentation
6. **Interactive HTML Reports** - Generates beautiful HTML reports with SVG diagrams

## How to use

### Method 1: Web Interface (Recommended)

1. Start the backend server:
```bash
cd backend
# Install dependencies if not already done
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

2. Start the frontend:
```bash
cd frontend
# Install dependencies if not already done
npm install

# Start the dev server
npm run dev
```

3. Open your browser and navigate to: `http://localhost:5173/architecture`

4. Click the "分析本地仓库" (Analyze Local Repository) button

5. View the generated reports:
   - Full HTML report with interactive tabs
   - Service topology SVG diagram
   - Architecture pattern distribution chart

### Method 2: API Endpoint

```bash
# Analyze the local repository
curl -X POST http://localhost:8000/api/architecture/analyze-local

# The response will include URLs to view the generated reports
```

### Method 3: Test Script

```bash
cd backend
python test_architecture_audit.py
```

## What the system analyzes

### 1. Architecture Patterns
The system scans your codebase for:
- Directory structure (e.g., models/, views/, controllers/)
- File naming patterns (e.g., *Service.py, *Repository.java)
- Code keywords (e.g., @Controller, UseCase, Aggregate)

Detected patterns include:
- MVC (Model-View-Controller)
- Hexagonal Architecture
- Clean Architecture
- Domain-Driven Design (DDD)
- Layered Architecture
- Event-Driven Architecture

### 2. API Endpoints
Extracts API definitions from:
- **REST**: FastAPI (@app.get), Flask, Spring (@GetMapping), Express (router.get)
- **gRPC**: Proto files (rpc methods)
- **GraphQL**: Schema definitions (type Query, type Mutation)

### 3. Service Dependencies
Identifies service calls through:
- HTTP client libraries (requests, fetch, axios, HttpClient)
- gRPC stubs
- Message queue publishers/subscribers (RabbitMQ, Kafka)

Detects issues:
- Circular dependencies (A→B→C→A)
- Performance bottlenecks (services with >5 incoming connections)
- Sync call chains (potential latency accumulation)

### 4. Technology Stack
Analyzes package files:
- Python: requirements.txt
- Node.js: package.json
- Java: pom.xml
- Go: go.mod
- .NET: .csproj

Categories:
- Databases (PostgreSQL, MySQL, MongoDB, Redis)
- Message Queues (RabbitMQ, Kafka, NATS)
- Caches (Redis, Memcached)
- Web Frameworks (FastAPI, Express, Spring Boot)
- Programming Languages

## Generated Reports

### HTML Report Structure
The interactive HTML report contains multiple tabs:

1. **概览 (Overview)** - Summary statistics and key findings
2. **架构模式 (Patterns)** - Architecture pattern distribution and confidence scores
3. **API契约 (API Contract)** - API endpoints, breaking changes, and standards violations
4. **服务拓扑 (Topology)** - Service dependencies, circular dependencies, and bottlenecks
5. **技术栈 (Tech Stack)** - Technology inventory, version conflicts, and standardization recommendations
6. **ADR模板 (ADR Template)** - Architecture Decision Record template and usage guide

### SVG Diagrams

1. **Topology Diagram** - Visual representation of service dependencies
   - Blue arrows: Synchronous calls
   - Green arrows: Asynchronous calls
   - Red nodes: Circular dependencies
   - Orange nodes: Performance bottlenecks

2. **Pattern Distribution Chart** - Bar chart showing architecture pattern usage

## Example Output

When you analyze the current repository, you'll see:

```
📊 Summary:
  - Total Repositories: 1
  - Total Services: 2 (backend, frontend)
  - Total Endpoints: 9
  - Circular Dependencies: 0
  - Performance Bottlenecks: 0

🏛️ Detected Architecture Patterns:
  - MVC (confidence: 0.70)
  - Hexagonal (confidence: 0.44)
  - Clean Architecture (confidence: 0.40)

🔌 Detected API Endpoints:
  - GET /api/health
  - GET /api/models
  - POST /api/detect/image
  - POST /api/detect/video
  - POST /api/architecture/analyze-local

🛠️ Technology Stack:
  - FastAPI 0.109.0 (Web Framework)
  - Vue 3 (Web Framework)
  - PyTorch 2.1.1 (Other)
```

## Extending the System

### Add New Architecture Patterns

Edit `backend/app/architecture/analyzers/pattern_detector.py`:

```python
self.pattern_indicators = {
    ArchitecturePattern.YOUR_PATTERN: {
        'directories': ['your_dir1', 'your_dir2'],
        'files': ['pattern_file'],
        'keywords': ['YourKeyword', '@YourAnnotation']
    },
}
```

### Customize Detection Thresholds

In `pattern_detector.py`:
```python
if score >= 0.3:  # Adjust this threshold
    detected_patterns.append(pattern)
```

In `topology_analyzer.py`:
```python
if count >= 5:  # Adjust bottleneck threshold
    bottlenecks.append(...)
```

## Troubleshooting

### No patterns detected
- Make sure your codebase has recognizable directory structures
- Check that file naming follows common conventions
- The system requires at least 30% confidence to report a pattern

### No API endpoints found
- Ensure your API definitions use standard frameworks
- Check that API routes are defined in code files (not config only)

### Empty topology diagram
- The system needs to find HTTP calls, gRPC stubs, or message queue operations
- Make sure service dependencies are explicit in code

## Additional Resources

- Full documentation: `backend/ARCHITECTURE_AUDIT_README.md`
- Test script: `backend/test_architecture_audit.py`
- Data models: `backend/app/architecture/models/architecture_models.py`
- Frontend component: `frontend/src/views/ArchitectureAudit.vue`

## Next Steps

1. Run the analysis on your actual microservice repositories
2. Review the generated reports
3. Address identified issues (circular dependencies, bottlenecks, version conflicts)
4. Use the ADR template to document architecture decisions
5. Re-run analysis regularly to track improvements
