"""
SVG Diagram Generator
Generates SVG diagrams for architecture visualization
"""
from typing import List, Dict, Set, Tuple
import math

from app.architecture.models.architecture_models import SystemTopology, ServiceDependency


class SVGDiagramGenerator:
    """Generates SVG diagrams for architecture visualization"""
    
    def __init__(self, width: int = 1200, height: int = 800):
        self.width = width
        self.height = height
        self.node_radius = 30
        self.colors = {
            'sync': '#667eea',
            'async': '#4caf50',
            'event': '#ff9800',
            'circular': '#f44336',
            'bottleneck': '#ff5722'
        }
    
    def generate_topology_diagram(self, topology: SystemTopology) -> str:
        """Generate SVG diagram for service topology"""
        # Calculate node positions using force-directed layout approximation
        positions = self._calculate_positions(topology.services, topology.dependencies)
        
        # Build SVG
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <marker id="arrowhead-sync" markerWidth="10" markerHeight="10" 
                refX="9" refY="3" orient="auto">
            <polygon points="0 0, 10 3, 0 6" fill="{self.colors['sync']}" />
        </marker>
        <marker id="arrowhead-async" markerWidth="10" markerHeight="10" 
                refX="9" refY="3" orient="auto">
            <polygon points="0 0, 10 3, 0 6" fill="{self.colors['async']}" />
        </marker>
        <filter id="shadow">
            <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
        </filter>
    </defs>
    
    <!-- Background -->
    <rect width="{self.width}" height="{self.height}" fill="#f5f5f5"/>
    
    <!-- Title -->
    <text x="{self.width // 2}" y="30" text-anchor="middle" 
          font-size="24" font-weight="bold" fill="#333">
        服务拓扑图
    </text>
    
    <!-- Dependencies (edges) -->
    <g id="dependencies">
'''
        
        # Draw dependencies
        circular_services = set()
        for circular in topology.circular_dependencies:
            circular_services.update(circular.services)
        
        bottleneck_services = {b.service_name for b in topology.bottlenecks}
        
        for dep in topology.dependencies:
            if dep.source_service in positions and dep.target_service in positions:
                x1, y1 = positions[dep.source_service]
                x2, y2 = positions[dep.target_service]
                
                # Determine edge color
                if dep.source_service in circular_services and dep.target_service in circular_services:
                    color = self.colors['circular']
                    marker = 'arrowhead-sync'
                    width = 3
                elif dep.dependency_type == 'async':
                    color = self.colors['async']
                    marker = 'arrowhead-async'
                    width = 2
                else:
                    color = self.colors['sync']
                    marker = 'arrowhead-sync'
                    width = 2
                
                # Draw edge with curve for better visibility
                svg += f'''        <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" 
              stroke="{color}" stroke-width="{width}" 
              marker-end="url(#{marker})" opacity="0.6"/>
'''
        
        svg += '''    </g>
    
    <!-- Services (nodes) -->
    <g id="services">
'''
        
        # Draw service nodes
        for service, (x, y) in positions.items():
            # Determine node color based on status
            if service in bottleneck_services:
                fill_color = self.colors['bottleneck']
                stroke_color = '#d32f2f'
            elif service in circular_services:
                fill_color = self.colors['circular']
                stroke_color = '#c62828'
            else:
                fill_color = '#ffffff'
                stroke_color = self.colors['sync']
            
            svg += f'''        <g class="service-node">
            <circle cx="{x}" cy="{y}" r="{self.node_radius}" 
                    fill="{fill_color}" stroke="{stroke_color}" 
                    stroke-width="3" filter="url(#shadow)"/>
            <text x="{x}" y="{y + 5}" text-anchor="middle" 
                  font-size="12" font-weight="bold" fill="#333">
                {service[:15]}
            </text>
        </g>
'''
        
        svg += '''    </g>
    
    <!-- Legend -->
    <g id="legend" transform="translate(50, ''' + str(self.height - 150) + ''')">
        <rect width="200" height="120" fill="white" stroke="#ddd" 
              stroke-width="1" rx="5" filter="url(#shadow)"/>
        <text x="10" y="20" font-size="14" font-weight="bold">图例</text>
        
        <circle cx="20" cy="40" r="8" fill="white" stroke="''' + self.colors['sync'] + '''" stroke-width="2"/>
        <text x="35" y="45" font-size="12">正常服务</text>
        
        <circle cx="20" cy="60" r="8" fill="''' + self.colors['bottleneck'] + '''" stroke="#d32f2f" stroke-width="2"/>
        <text x="35" y="65" font-size="12">性能瓶颈</text>
        
        <circle cx="20" cy="80" r="8" fill="''' + self.colors['circular'] + '''" stroke="#c62828" stroke-width="2"/>
        <text x="35" y="85" font-size="12">循环依赖</text>
        
        <line x1="10" y1="100" x2="50" y2="100" stroke="''' + self.colors['sync'] + '''" stroke-width="2" marker-end="url(#arrowhead-sync)"/>
        <text x="55" y="105" font-size="12">同步调用</text>
        
        <line x1="110" y1="100" x2="150" y2="100" stroke="''' + self.colors['async'] + '''" stroke-width="2" marker-end="url(#arrowhead-async)"/>
        <text x="155" y="105" font-size="12">异步调用</text>
    </g>
</svg>'''
        
        return svg
    
    def _calculate_positions(self, services: List[str], 
                            dependencies: List[ServiceDependency]) -> Dict[str, Tuple[float, float]]:
        """Calculate node positions using circular layout"""
        positions = {}
        
        # Filter out topic nodes
        real_services = [s for s in services if not s.startswith('topic:')]
        
        if not real_services:
            return positions
        
        # Use circular layout
        center_x = self.width // 2
        center_y = self.height // 2
        radius = min(self.width, self.height) * 0.35
        
        n = len(real_services)
        for i, service in enumerate(real_services):
            angle = 2 * math.pi * i / n - math.pi / 2  # Start from top
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle) + 50  # Offset for title
            positions[service] = (x, y)
        
        return positions
    
    def generate_pattern_distribution_chart(self, pattern_counts: Dict[str, int]) -> str:
        """Generate SVG bar chart for pattern distribution"""
        width = 800
        height = 400
        margin = 50
        bar_width = 60
        
        max_count = max(pattern_counts.values()) if pattern_counts else 1
        
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <rect width="{width}" height="{height}" fill="#f5f5f5"/>
    
    <text x="{width // 2}" y="30" text-anchor="middle" 
          font-size="20" font-weight="bold">
        架构模式分布
    </text>
    
    <!-- Y-axis -->
    <line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" 
          stroke="#333" stroke-width="2"/>
    
    <!-- X-axis -->
    <line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" 
          stroke="#333" stroke-width="2"/>
    
    <!-- Bars -->
'''
        
        x_pos = margin + 40
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
            bar_height = (count / max_count) * (height - 2 * margin - 50)
            y_pos = height - margin - bar_height
            
            svg += f'''    <rect x="{x_pos}" y="{y_pos}" width="{bar_width}" height="{bar_height}" 
          fill="#667eea" opacity="0.8"/>
    <text x="{x_pos + bar_width // 2}" y="{y_pos - 5}" 
          text-anchor="middle" font-size="12" font-weight="bold">
        {count}
    </text>
    <text x="{x_pos + bar_width // 2}" y="{height - margin + 20}" 
          text-anchor="middle" font-size="10" transform="rotate(-45, {x_pos + bar_width // 2}, {height - margin + 20})">
        {pattern[:15]}
    </text>
'''
            x_pos += bar_width + 30
        
        svg += '</svg>'
        return svg
