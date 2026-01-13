"""
HTML Report Generator
Generates interactive HTML reports with architecture visualizations
"""
import json
from typing import List
from datetime import datetime

from app.architecture.models.architecture_models import (
    ArchitectureAuditReport, RepositoryAnalysis, SystemTopology
)


class HTMLReportGenerator:
    """Generates interactive HTML reports"""
    
    def generate_report(self, report: ArchitectureAuditReport) -> str:
        """Generate complete HTML report"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>架构一致性审计报告</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏗️ 架构一致性审计报告</h1>
            <div class="meta">
                <span>生成时间: {report.timestamp}</span>
                <span>总仓库数: {report.total_repositories}</span>
                <span>总服务数: {report.total_services}</span>
            </div>
        </header>
        
        <nav class="tabs">
            <button class="tab-btn active" onclick="showTab('overview')">概览</button>
            <button class="tab-btn" onclick="showTab('patterns')">架构模式</button>
            <button class="tab-btn" onclick="showTab('api')">API契约</button>
            <button class="tab-btn" onclick="showTab('topology')">服务拓扑</button>
            <button class="tab-btn" onclick="showTab('techstack')">技术栈</button>
            <button class="tab-btn" onclick="showTab('adr')">ADR模板</button>
        </nav>
        
        <div id="overview" class="tab-content active">
            {self._generate_overview_section(report)}
        </div>
        
        <div id="patterns" class="tab-content">
            {self._generate_patterns_section(report.repositories)}
        </div>
        
        <div id="api" class="tab-content">
            {self._generate_api_section(report.api_report, report.repositories)}
        </div>
        
        <div id="topology" class="tab-content">
            {self._generate_topology_section(report.topology)}
        </div>
        
        <div id="techstack" class="tab-content">
            {self._generate_techstack_section(report.tech_stack_report)}
        </div>
        
        <div id="adr" class="tab-content">
            {self._generate_adr_section()}
        </div>
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""
        return html
    
    def _get_css(self) -> str:
        """Get CSS styles"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
        }
        
        .meta {
            display: flex;
            justify-content: center;
            gap: 30px;
            font-size: 1.1rem;
        }
        
        .tabs {
            display: flex;
            background: #f5f5f5;
            border-bottom: 2px solid #ddd;
        }
        
        .tab-btn {
            flex: 1;
            padding: 15px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s;
        }
        
        .tab-btn:hover {
            background: #e0e0e0;
        }
        
        .tab-btn.active {
            background: white;
            border-bottom: 3px solid #667eea;
            font-weight: bold;
        }
        
        .tab-content {
            display: none;
            padding: 40px;
            animation: fadeIn 0.5s;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .card {
            background: #f9f9f9;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5rem;
        }
        
        .card h3 {
            color: #764ba2;
            margin: 15px 0 10px 0;
            font-size: 1.2rem;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-box {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        
        .pattern-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .pattern-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .confidence-bar {
            background: #e0e0e0;
            height: 8px;
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.5s;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .alert-high {
            background: #ffebee;
            border-left: 4px solid #f44336;
        }
        
        .alert-medium {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
        }
        
        .alert-low {
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background: #667eea;
            color: white;
            font-weight: bold;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .code-link {
            color: #667eea;
            text-decoration: none;
            font-family: monospace;
        }
        
        .code-link:hover {
            text-decoration: underline;
        }
        
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: bold;
            margin: 2px;
        }
        
        .badge-primary {
            background: #667eea;
            color: white;
        }
        
        .badge-success {
            background: #4caf50;
            color: white;
        }
        
        .badge-warning {
            background: #ff9800;
            color: white;
        }
        
        .badge-danger {
            background: #f44336;
            color: white;
        }
        
        #topology-diagram {
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: white;
            margin: 20px 0;
        }
        """
    
    def _get_javascript(self) -> str:
        """Get JavaScript code"""
        return """
        function showTab(tabName) {
            // Hide all tabs
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        // Initialize confidence bars animation
        window.addEventListener('load', () => {
            const bars = document.querySelectorAll('.confidence-fill');
            bars.forEach(bar => {
                const width = bar.getAttribute('data-width');
                setTimeout(() => {
                    bar.style.width = width + '%';
                }, 100);
            });
        });
        """
    
    def _generate_overview_section(self, report: ArchitectureAuditReport) -> str:
        """Generate overview section"""
        return f"""
        <div class="card">
            <h2>📊 审计概览</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="stat-value">{report.total_repositories}</div>
                    <div class="stat-label">仓库总数</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{report.total_services}</div>
                    <div class="stat-label">服务总数</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{report.api_report.total_endpoints}</div>
                    <div class="stat-label">API端点</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{len(report.topology.circular_dependencies)}</div>
                    <div class="stat-label">循环依赖</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{len(report.topology.bottlenecks)}</div>
                    <div class="stat-label">性能瓶颈</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{len(report.api_report.breaking_changes)}</div>
                    <div class="stat-label">破坏性变更</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🎯 关键发现</h2>
            {self._generate_key_findings(report)}
        </div>
        """
    
    def _generate_key_findings(self, report: ArchitectureAuditReport) -> str:
        """Generate key findings"""
        findings = []
        
        if report.topology.circular_dependencies:
            findings.append(f'<div class="alert alert-high">⚠️ 发现 {len(report.topology.circular_dependencies)} 个循环依赖</div>')
        
        if report.topology.bottlenecks:
            high_severity = len([b for b in report.topology.bottlenecks if b.severity == "high"])
            if high_severity > 0:
                findings.append(f'<div class="alert alert-high">⚠️ 发现 {high_severity} 个高风险性能瓶颈</div>')
        
        if report.api_report.breaking_changes:
            findings.append(f'<div class="alert alert-medium">⚠️ 发现 {len(report.api_report.breaking_changes)} 个API破坏性变更</div>')
        
        if report.tech_stack_report.version_conflicts:
            findings.append(f'<div class="alert alert-medium">⚠️ 发现 {len(report.tech_stack_report.version_conflicts)} 个版本冲突</div>')
        
        if not findings:
            findings.append('<div class="alert alert-low">✅ 未发现重大问题</div>')
        
        return '\n'.join(findings)
    
    def _generate_patterns_section(self, repositories: List[RepositoryAnalysis]) -> str:
        """Generate architecture patterns section"""
        html = '<div class="card"><h2>🏛️ 架构模式分析</h2>'
        
        # Pattern distribution
        pattern_counts = {}
        for repo in repositories:
            for pattern in repo.architecture_patterns:
                pattern_name = pattern.value if hasattr(pattern, 'value') else str(pattern)
                pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1
        
        html += '<h3>模式分布</h3><div class="pattern-grid">'
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
            html += f'''
            <div class="pattern-item">
                <strong>{pattern}</strong>
                <div>使用次数: {count}</div>
            </div>
            '''
        html += '</div>'
        
        # Repository details
        html += '<h3>仓库详情</h3>'
        for repo in repositories:
            patterns_html = ' '.join([f'<span class="badge badge-primary">{p.value if hasattr(p, "value") else str(p)}</span>' 
                                     for p in repo.architecture_patterns])
            
            html += f'''
            <div class="card">
                <h3>📦 {repo.repo_name}</h3>
                <p><strong>仓库地址:</strong> <a href="{repo.repo_url}" class="code-link">{repo.repo_url}</a></p>
                <p><strong>架构模式:</strong> {patterns_html}</p>
                <p><strong>服务数:</strong> {len(repo.services)}</p>
            '''
            
            # Show confidence scores
            if repo.pattern_confidence:
                html += '<h4>置信度评分</h4>'
                for pattern, confidence in sorted(repo.pattern_confidence.items(), key=lambda x: x[1], reverse=True):
                    if confidence >= 0.3:
                        html += f'''
                        <div>
                            <strong>{pattern}:</strong>
                            <div class="confidence-bar">
                                <div class="confidence-fill" data-width="{confidence * 100}" style="width: 0%"></div>
                            </div>
                        </div>
                        '''
            
            html += '</div>'
        
        html += '</div>'
        return html
    
    def _generate_api_section(self, api_report, repositories: List[RepositoryAnalysis]) -> str:
        """Generate API contract section"""
        html = f'''
        <div class="card">
            <h2>🔌 API契约分析</h2>
            <p><strong>总端点数:</strong> {api_report.total_endpoints}</p>
        '''
        
        # Breaking changes
        if api_report.breaking_changes:
            html += '<h3>⚠️ 破坏性变更</h3>'
            for change in api_report.breaking_changes:
                severity_class = f"alert-{change.severity}"
                html += f'''
                <div class="alert {severity_class}">
                    <strong>{change.endpoint}</strong><br>
                    类型: {change.change_type}<br>
                    描述: {change.description}<br>
                    影响服务: {', '.join(change.affected_services)}
                </div>
                '''
        
        # API standards violations
        if api_report.api_standards_violations:
            html += '<h3>📋 标准违规</h3><ul>'
            for violation in api_report.api_standards_violations:
                html += f'<li>{violation}</li>'
            html += '</ul>'
        
        # API endpoints table
        html += '<h3>📑 API端点清单</h3><table><thead><tr>'
        html += '<th>服务</th><th>类型</th><th>方法</th><th>路径</th><th>文件位置</th>'
        html += '</tr></thead><tbody>'
        
        for repo in repositories:
            for endpoint in repo.api_endpoints[:50]:  # Limit to first 50
                api_type = endpoint.api_type.value if hasattr(endpoint.api_type, 'value') else str(endpoint.api_type)
                html += f'''
                <tr>
                    <td>{endpoint.service_name}</td>
                    <td><span class="badge badge-primary">{api_type}</span></td>
                    <td><span class="badge badge-success">{endpoint.method}</span></td>
                    <td><code>{endpoint.path}</code></td>
                    <td><span class="code-link">{endpoint.file_location or 'N/A'}</span></td>
                </tr>
                '''
        
        html += '</tbody></table></div>'
        return html
    
    def _generate_topology_section(self, topology: SystemTopology) -> str:
        """Generate topology section"""
        html = f'''
        <div class="card">
            <h2>🕸️ 服务拓扑分析</h2>
            <p><strong>总服务数:</strong> {len(topology.services)}</p>
            <p><strong>依赖关系数:</strong> {len(topology.dependencies)}</p>
        '''
        
        # Circular dependencies
        if topology.circular_dependencies:
            html += '<h3>⚠️ 循环依赖</h3>'
            for circular in topology.circular_dependencies:
                services_chain = ' → '.join(circular.services)
                html += f'''
                <div class="alert alert-high">
                    <strong>循环链:</strong> {services_chain}<br>
                    {circular.description}
                </div>
                '''
        
        # Performance bottlenecks
        if topology.bottlenecks:
            html += '<h3>🔥 性能瓶颈</h3>'
            for bottleneck in topology.bottlenecks:
                severity_class = f"alert-{bottleneck.severity}"
                html += f'''
                <div class="alert {severity_class}">
                    <strong>{bottleneck.service_name}</strong><br>
                    类型: {bottleneck.bottleneck_type}<br>
                    {bottleneck.description}
                </div>
                '''
        
        # Dependencies table
        html += '<h3>📊 依赖关系</h3><table><thead><tr>'
        html += '<th>源服务</th><th>目标服务</th><th>类型</th><th>置信度</th>'
        html += '</tr></thead><tbody>'
        
        for dep in topology.dependencies[:100]:  # Limit to first 100
            dep_type_badge = 'badge-success' if dep.dependency_type == 'async' else 'badge-primary'
            html += f'''
            <tr>
                <td>{dep.source_service}</td>
                <td>{dep.target_service}</td>
                <td><span class="badge {dep_type_badge}">{dep.dependency_type}</span></td>
                <td>{dep.confidence:.2f}</td>
            </tr>
            '''
        
        html += '</tbody></table>'
        
        # SVG diagram placeholder
        html += '''
        <h3>📈 拓扑可视化</h3>
        <div id="topology-diagram">
            <p style="padding: 20px; text-align: center; color: #666;">
                服务拓扑图将在此显示<br>
                （需要使用D3.js或类似库进行可视化）
            </p>
        </div>
        '''
        
        html += '</div>'
        return html
    
    def _generate_techstack_section(self, tech_report) -> str:
        """Generate tech stack section"""
        html = '<div class="card"><h2>🛠️ 技术栈分析</h2>'
        
        # Standardization recommendations
        if tech_report.standardization_recommendations:
            html += '<h3>💡 标准化建议</h3>'
            for rec in tech_report.standardization_recommendations:
                html += f'<div class="alert alert-medium">{rec}</div>'
        
        # Version conflicts
        if tech_report.version_conflicts:
            html += '<h3>⚠️ 版本冲突</h3>'
            for conflict in tech_report.version_conflicts:
                html += f'<div class="alert alert-high">{conflict}</div>'
        
        # Technology table
        html += '<h3>📦 技术清单</h3><table><thead><tr>'
        html += '<th>技术</th><th>版本</th><th>类别</th><th>服务</th>'
        html += '</tr></thead><tbody>'
        
        for tech in tech_report.tech_items[:100]:  # Limit to first 100
            category = tech.category.value if hasattr(tech.category, 'value') else str(tech.category)
            html += f'''
            <tr>
                <td><strong>{tech.name}</strong></td>
                <td>{tech.version or 'N/A'}</td>
                <td><span class="badge badge-primary">{category}</span></td>
                <td>{tech.service_name}</td>
            </tr>
            '''
        
        html += '</tbody></table></div>'
        return html
    
    def _generate_adr_section(self) -> str:
        """Generate ADR template section"""
        adr_template = """# ADR-XXXX: [决策标题]

## 状态
[提议 | 已接受 | 已废弃 | 已替代]

## 上下文
[描述需要做出决策的背景和问题]

## 决策
[描述做出的决策]

## 后果
### 积极影响
- [列出积极影响]

### 消极影响
- [列出可能的负面影响]

### 风险
- [列出相关风险]

## 备选方案
### 方案1: [方案名称]
- 优点: 
- 缺点: 

### 方案2: [方案名称]
- 优点: 
- 缺点: 

## 参考资料
- [相关文档链接]
- [相关讨论链接]

---
创建日期: YYYY-MM-DD
作者: [作者名称]
审核人: [审核人名称]"""
        
        return f'''
        <div class="card">
            <h2>📝 架构决策记录 (ADR) 模板</h2>
            <p>使用以下模板统一所有仓库的架构决策文档：</p>
            <pre>{adr_template}</pre>
            
            <h3>💡 使用指南</h3>
            <ul>
                <li>每个重要的架构决策都应创建一个ADR文档</li>
                <li>ADR文档应存储在仓库的 <code>/docs/adr/</code> 目录下</li>
                <li>使用递增的数字编号，如 <code>ADR-0001.md</code></li>
                <li>决策一旦做出，ADR文档不应修改，而应创建新的ADR来替代</li>
                <li>包含足够的上下文信息，使未来的开发者能理解决策背景</li>
            </ul>
            
            <h3>📂 推荐的文档结构</h3>
            <pre>
repository/
├── docs/
│   ├── adr/
│   │   ├── README.md
│   │   ├── ADR-0001-选择FastAPI作为Web框架.md
│   │   ├── ADR-0002-采用PostgreSQL数据库.md
│   │   └── ADR-0003-使用Redis作为缓存层.md
│   ├── architecture/
│   │   └── system-design.md
│   └── api/
│       └── api-spec.yaml
            </pre>
        </div>
        '''
