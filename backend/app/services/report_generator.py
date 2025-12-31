"""
HTML Report Generator
Generates interactive HTML reports with architecture visualizations
"""

from typing import Dict, List
from datetime import datetime


class HTMLReportGenerator:
    """Generates interactive HTML reports for architecture audits"""
    
    def __init__(self):
        self.template = self._get_html_template()
    
    def generate_report(
        self,
        architecture_data: Dict,
        api_data: Dict,
        tech_stack_data: Dict,
        topology_data: Dict = None
    ) -> str:
        """Generate complete HTML report"""
        
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build report sections
        architecture_section = self._build_architecture_section(architecture_data)
        api_section = self._build_api_section(api_data)
        tech_stack_section = self._build_tech_stack_section(tech_stack_data)
        topology_section = self._build_topology_section(topology_data) if topology_data else ""
        adr_section = self._build_adr_template_section()
        
        # Combine all sections
        html = self.template.format(
            report_date=report_date,
            architecture_section=architecture_section,
            api_section=api_section,
            tech_stack_section=tech_stack_section,
            topology_section=topology_section,
            adr_section=adr_section
        )
        
        return html
    
    def _build_architecture_section(self, data: Dict) -> str:
        """Build architecture patterns section"""
        structure = data.get('structure', {})
        patterns = data.get('detected_patterns', [])
        components = data.get('components', {})
        
        patterns_html = ""
        for pattern in patterns:
            confidence_percent = pattern['confidence'] * 100
            confidence_class = "high" if confidence_percent > 60 else "medium" if confidence_percent > 30 else "low"
            
            indicators_html = "".join([
                f"<li>{indicator}</li>"
                for indicator in pattern['indicators'][:5]
            ])
            
            patterns_html += f"""
            <div class="pattern-card">
                <h3>{pattern['name']} <span class="confidence {confidence_class}">{confidence_percent:.0f}% confidence</span></h3>
                <ul class="indicators">{indicators_html}</ul>
            </div>
            """
        
        components_html = ""
        for component_type, files in components.items():
            if files:
                files_list = "".join([f"<li>{f}</li>" for f in files[:10]])
                components_html += f"""
                <div class="component-group">
                    <h4>{component_type.replace('_', ' ').title()} ({len(files)})</h4>
                    <ul class="file-list">{files_list}</ul>
                    {f'<p class="more">...and {len(files) - 10} more</p>' if len(files) > 10 else ''}
                </div>
                """
        
        return f"""
        <section id="architecture" class="section">
            <h2>📐 Architecture Patterns Analysis</h2>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{structure.get('total_files', 0)}</h3>
                    <p>Total Files</p>
                </div>
                <div class="stat-card">
                    <h3>{structure.get('python_files', 0)}</h3>
                    <p>Python Files</p>
                </div>
                <div class="stat-card">
                    <h3>{structure.get('javascript_files', 0)}</h3>
                    <p>JS/TS Files</p>
                </div>
                <div class="stat-card">
                    <h3>{len(patterns)}</h3>
                    <p>Patterns Detected</p>
                </div>
            </div>
            
            <h3>Detected Patterns</h3>
            <div class="patterns-container">
                {patterns_html if patterns_html else '<p class="empty">No architecture patterns detected</p>'}
            </div>
            
            <h3>Key Components</h3>
            <div class="components-container">
                {components_html if components_html else '<p class="empty">No components identified</p>'}
            </div>
        </section>
        """
    
    def _build_api_section(self, data: Dict) -> str:
        """Build API contracts section"""
        summary = data.get('summary', {})
        contracts = data.get('api_contracts', [])
        
        contracts_html = ""
        for contract in contracts:
            endpoints = contract.get('endpoints', [])
            framework = contract.get('framework', 'Unknown')
            
            endpoints_html = ""
            for ep in endpoints[:20]:  # Limit to 20 endpoints
                method_class = ep.get('method', 'GET').lower()
                endpoints_html += f"""
                <tr>
                    <td><span class="method {method_class}">{ep.get('method', 'GET')}</span></td>
                    <td><code>{ep.get('path', '/')}</code></td>
                    <td>{ep.get('handler', '-')}</td>
                    <td class="file-path">{ep.get('file', '-')}</td>
                </tr>
                """
            
            contracts_html += f"""
            <div class="contract-card">
                <h3>{contract['type']} API - {framework}</h3>
                <p class="contract-info">Found {len(endpoints)} endpoints</p>
                <table class="endpoints-table">
                    <thead>
                        <tr>
                            <th>Method</th>
                            <th>Path</th>
                            <th>Handler</th>
                            <th>File</th>
                        </tr>
                    </thead>
                    <tbody>
                        {endpoints_html}
                    </tbody>
                </table>
                {f'<p class="more">...and {len(endpoints) - 20} more endpoints</p>' if len(endpoints) > 20 else ''}
            </div>
            """
        
        return f"""
        <section id="api-contracts" class="section">
            <h2>🔌 API Contracts Analysis</h2>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{summary.get('total_endpoints', 0)}</h3>
                    <p>Total Endpoints</p>
                </div>
                <div class="stat-card">
                    <h3>{len(summary.get('api_types', []))}</h3>
                    <p>API Types</p>
                </div>
                <div class="stat-card">
                    <h3>{len(summary.get('frameworks_detected', []))}</h3>
                    <p>Frameworks</p>
                </div>
            </div>
            
            <div class="contracts-container">
                {contracts_html if contracts_html else '<p class="empty">No API contracts detected</p>'}
            </div>
        </section>
        """
    
    def _build_tech_stack_section(self, data: Dict) -> str:
        """Build technology stack section"""
        stack = data.get('technology_stack', {})
        recommendations = data.get('recommendations', [])
        
        def build_tech_list(items):
            if not items:
                return '<p class="empty-tech">None detected</p>'
            return ''.join([f'<span class="tech-badge">{item}</span>' for item in items])
        
        recommendations_html = ''.join([
            f'<li class="recommendation">{rec}</li>'
            for rec in recommendations
        ])
        
        return f"""
        <section id="tech-stack" class="section">
            <h2>🛠️ Technology Stack Audit</h2>
            
            <div class="tech-grid">
                <div class="tech-category">
                    <h3>Databases</h3>
                    <div class="tech-list">
                        {build_tech_list(stack.get('databases', []))}
                    </div>
                </div>
                <div class="tech-category">
                    <h3>Message Queues</h3>
                    <div class="tech-list">
                        {build_tech_list(stack.get('message_queues', []))}
                    </div>
                </div>
                <div class="tech-category">
                    <h3>Caches</h3>
                    <div class="tech-list">
                        {build_tech_list(stack.get('caches', []))}
                    </div>
                </div>
                <div class="tech-category">
                    <h3>Web Frameworks</h3>
                    <div class="tech-list">
                        {build_tech_list(stack.get('web_frameworks', []))}
                    </div>
                </div>
                <div class="tech-category">
                    <h3>Languages</h3>
                    <div class="tech-list">
                        {build_tech_list(list(stack.get('languages', {}).keys()))}
                    </div>
                </div>
                <div class="tech-category">
                    <h3>Containerization</h3>
                    <div class="tech-list">
                        {build_tech_list(stack.get('containerization', []))}
                    </div>
                </div>
                <div class="tech-category">
                    <h3>CI/CD</h3>
                    <div class="tech-list">
                        {build_tech_list(stack.get('ci_cd', []))}
                    </div>
                </div>
            </div>
            
            {f'''
            <h3>Recommendations</h3>
            <ul class="recommendations-list">
                {recommendations_html}
            </ul>
            ''' if recommendations else ''}
        </section>
        """
    
    def _build_topology_section(self, data: Dict) -> str:
        """Build system topology section"""
        return """
        <section id="topology" class="section">
            <h2>🌐 System Topology</h2>
            <div class="topology-placeholder">
                <p>System topology diagram generation requires scanning multiple service repositories.</p>
                <p>This feature analyzes service dependencies and generates an interactive topology visualization.</p>
            </div>
        </section>
        """
    
    def _build_adr_template_section(self) -> str:
        """Build ADR template section"""
        adr_template = """# ADR-{number}: {Title}

## Status
{Proposed | Accepted | Deprecated | Superseded}

## Context
{Describe the context and problem statement that led to this decision}

## Decision
{Describe the decision that was made}

## Consequences
### Positive
- {Positive consequence 1}
- {Positive consequence 2}

### Negative
- {Negative consequence 1}
- {Negative consequence 2}

## Alternatives Considered
1. **Alternative 1**: {Description}
   - Pros: {pros}
   - Cons: {cons}

2. **Alternative 2**: {Description}
   - Pros: {pros}
   - Cons: {cons}

## References
- {Link or reference 1}
- {Link or reference 2}

## Date
{YYYY-MM-DD}

## Authors
{Author name(s)}
"""
        
        return f"""
        <section id="adr-template" class="section">
            <h2>📝 Architecture Decision Records (ADR) Template</h2>
            <p>Use this template to document architectural decisions across all repositories:</p>
            <div class="adr-template">
                <pre><code>{adr_template}</code></pre>
            </div>
            <button class="download-btn" onclick="downloadADR()">Download ADR Template</button>
        </section>
        """
    
    def _get_html_template(self) -> str:
        """Get HTML template with styles and scripts"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Architecture Audit Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        nav {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 20px;
            z-index: 100;
        }}
        
        nav ul {{
            list-style: none;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        
        nav a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            padding: 8px 16px;
            border-radius: 5px;
            transition: background 0.3s;
        }}
        
        nav a:hover {{
            background: #f0f0f0;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8rem;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .stat-card h3 {{
            font-size: 2.5rem;
            margin-bottom: 5px;
        }}
        
        .stat-card p {{
            opacity: 0.9;
            font-size: 0.9rem;
        }}
        
        .pattern-card {{
            border: 2px solid #e0e0e0;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            transition: border-color 0.3s;
        }}
        
        .pattern-card:hover {{
            border-color: #667eea;
        }}
        
        .pattern-card h3 {{
            color: #333;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .confidence {{
            font-size: 0.9rem;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: normal;
        }}
        
        .confidence.high {{
            background: #4caf50;
            color: white;
        }}
        
        .confidence.medium {{
            background: #ff9800;
            color: white;
        }}
        
        .confidence.low {{
            background: #f44336;
            color: white;
        }}
        
        .indicators {{
            list-style: none;
            padding-left: 0;
        }}
        
        .indicators li {{
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }}
        
        .indicators li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #4caf50;
            font-weight: bold;
        }}
        
        .component-group {{
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
        }}
        
        .component-group h4 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .file-list {{
            list-style: none;
            padding-left: 0;
        }}
        
        .file-list li {{
            padding: 3px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            color: #666;
        }}
        
        .contract-card {{
            border: 2px solid #e0e0e0;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
        }}
        
        .endpoints-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        
        .endpoints-table th {{
            background: #f0f0f0;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .endpoints-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .endpoints-table tr:hover {{
            background: #f9f9f9;
        }}
        
        .method {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85rem;
            font-weight: 600;
            color: white;
        }}
        
        .method.get {{
            background: #4caf50;
        }}
        
        .method.post {{
            background: #2196f3;
        }}
        
        .method.put {{
            background: #ff9800;
        }}
        
        .method.delete {{
            background: #f44336;
        }}
        
        .method.patch {{
            background: #9c27b0;
        }}
        
        .file-path {{
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            color: #666;
        }}
        
        .tech-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .tech-category {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
        }}
        
        .tech-category h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.1rem;
        }}
        
        .tech-badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 12px;
            margin: 5px;
            border-radius: 20px;
            font-size: 0.9rem;
        }}
        
        .recommendations-list {{
            list-style: none;
            padding: 0;
        }}
        
        .recommendation {{
            padding: 15px;
            margin: 10px 0;
            background: #fff3cd;
            border-left: 4px solid #ff9800;
            border-radius: 5px;
        }}
        
        .adr-template {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            overflow-x: auto;
        }}
        
        .adr-template pre {{
            margin: 0;
            white-space: pre-wrap;
        }}
        
        .download-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            transition: background 0.3s;
        }}
        
        .download-btn:hover {{
            background: #764ba2;
        }}
        
        .empty {{
            text-align: center;
            color: #999;
            padding: 40px;
            font-style: italic;
        }}
        
        .empty-tech {{
            color: #999;
            font-style: italic;
        }}
        
        .more {{
            color: #666;
            font-style: italic;
            margin-top: 10px;
        }}
        
        .topology-placeholder {{
            text-align: center;
            padding: 60px 20px;
            background: #f9f9f9;
            border-radius: 10px;
            color: #666;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏗️ Architecture Audit Report</h1>
            <p>Generated on {report_date}</p>
        </header>
        
        <nav>
            <ul>
                <li><a href="#architecture">Architecture Patterns</a></li>
                <li><a href="#api-contracts">API Contracts</a></li>
                <li><a href="#tech-stack">Technology Stack</a></li>
                <li><a href="#topology">System Topology</a></li>
                <li><a href="#adr-template">ADR Template</a></li>
            </ul>
        </nav>
        
        {architecture_section}
        
        {api_section}
        
        {tech_stack_section}
        
        {topology_section}
        
        {adr_section}
        
        <footer>
            <p>Generated by Argus-IIoT Architecture Audit Tool</p>
        </footer>
    </div>
    
    <script>
        function downloadADR() {{
            const adrTemplate = `# ADR-{{number}}: {{Title}}

## Status
{{Proposed | Accepted | Deprecated | Superseded}}

## Context
{{Describe the context and problem statement that led to this decision}}

## Decision
{{Describe the decision that was made}}

## Consequences
### Positive
- {{Positive consequence 1}}
- {{Positive consequence 2}}

### Negative
- {{Negative consequence 1}}
- {{Negative consequence 2}}

## Alternatives Considered
1. **Alternative 1**: {{Description}}
   - Pros: {{pros}}
   - Cons: {{cons}}

2. **Alternative 2**: {{Description}}
   - Pros: {{pros}}
   - Cons: {{cons}}

## References
- {{Link or reference 1}}
- {{Link or reference 2}}

## Date
{{YYYY-MM-DD}}

## Authors
{{Author name(s)}}`;
            
            const blob = new Blob([adrTemplate], {{ type: 'text/markdown' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'ADR-template.md';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
        
        // Smooth scrolling for navigation
        document.querySelectorAll('nav a').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>
"""


# Singleton instance
html_report_generator = HTMLReportGenerator()
