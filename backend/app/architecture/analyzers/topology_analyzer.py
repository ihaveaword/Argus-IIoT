"""
Service Topology Analyzer
Analyzes service dependencies and call patterns
"""
import os
import re
from typing import List, Dict, Set, Tuple
from collections import defaultdict

from app.architecture.models.architecture_models import (
    ServiceDependency, SystemTopology, CircularDependency, PerformanceBottleneck
)


class TopologyAnalyzer:
    """Analyzes service topology and dependencies"""
    
    def __init__(self):
        # Patterns for detecting service calls
        self.http_call_patterns = [
            r'requests\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)',  # Python requests
            r'fetch\(["\']([^"\']+)["\']\)',  # JavaScript fetch
            r'axios\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)',  # Axios
            r'HttpClient\.\w+\(["\']([^"\']+)["\']\)',  # .NET HttpClient
            r'RestTemplate\.\w+\(["\']([^"\']+)["\']\)',  # Spring RestTemplate
        ]
        
        self.grpc_call_patterns = [
            r'(\w+)Stub\(',  # gRPC stub
            r'\.newStub\(',
        ]
        
        self.message_queue_patterns = [
            r'publish\(["\']([^"\']+)["\']\)',  # Message publishing
            r'subscribe\(["\']([^"\']+)["\']\)',  # Message subscription
            r'send\(["\']([^"\']+)["\']\)',  # Message sending
            r'@RabbitListener',  # RabbitMQ
            r'@KafkaListener',  # Kafka
        ]
    
    def extract_service_calls(self, content: str, source_service: str) -> List[ServiceDependency]:
        """Extract service calls from code"""
        dependencies = []
        
        # Extract HTTP calls
        for pattern in self.http_call_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Try to extract service name from URL
                url = match.group(1) if len(match.groups()) == 1 else match.group(2)
                target_service = self._extract_service_from_url(url)
                
                if target_service and target_service != source_service:
                    dependencies.append(ServiceDependency(
                        source_service=source_service,
                        target_service=target_service,
                        dependency_type="sync",
                        confidence=0.8
                    ))
        
        # Extract gRPC calls
        for pattern in self.grpc_call_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                service_name = match.group(1) if match.lastindex >= 1 else "unknown"
                if service_name != "unknown":
                    dependencies.append(ServiceDependency(
                        source_service=source_service,
                        target_service=service_name,
                        dependency_type="sync",
                        confidence=0.7
                    ))
        
        # Extract message queue patterns
        for pattern in self.message_queue_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Message queue communications are async
                topic = match.group(1) if match.lastindex >= 1 else "unknown_topic"
                dependencies.append(ServiceDependency(
                    source_service=source_service,
                    target_service=f"topic:{topic}",
                    dependency_type="async",
                    confidence=0.6
                ))
        
        return dependencies
    
    def _extract_service_from_url(self, url: str) -> str:
        """Extract service name from URL"""
        # Remove protocol
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^//', '', url)
        
        # Extract hostname/service name
        parts = url.split('/')[0].split(':')[0]
        
        # Common service name patterns
        if parts.startswith('localhost') or parts.startswith('127.0.0.1'):
            # Try to extract from path
            path_match = re.search(r'/api/([^/]+)', url)
            if path_match:
                return path_match.group(1)
            return "localhost"
        
        # Extract service name from hostname
        service_name = parts.split('.')[0]
        return service_name if service_name else "unknown"
    
    def analyze_repository(self, repo_path: str, service_name: str) -> List[ServiceDependency]:
        """Analyze repository for service dependencies"""
        all_dependencies = []
        
        if not os.path.exists(repo_path):
            return all_dependencies
        
        for root, dirs, files in os.walk(repo_path):
            # Skip non-source directories
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '__pycache__', '.git', 'dist', 'build']]
            
            for file_name in files:
                if not file_name.endswith(('.py', '.java', '.js', '.ts', '.go')):
                    continue
                
                file_path = os.path.join(root, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        dependencies = self.extract_service_calls(content, service_name)
                        all_dependencies.extend(dependencies)
                except Exception:
                    continue
        
        return all_dependencies
    
    def detect_circular_dependencies(self, dependencies: List[ServiceDependency]) -> List[CircularDependency]:
        """Detect circular dependencies in service graph"""
        circular_deps = []
        
        # Build adjacency list
        graph = defaultdict(set)
        for dep in dependencies:
            if not dep.target_service.startswith('topic:'):
                graph[dep.source_service].add(dep.target_service)
        
        # DFS to detect cycles
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    circular_deps.append(CircularDependency(
                        services=cycle,
                        description=f"Circular dependency detected: {' -> '.join(cycle)}"
                    ))
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                dfs(node)
                path = []
                rec_stack = set()
        
        return circular_deps
    
    def detect_bottlenecks(self, dependencies: List[ServiceDependency]) -> List[PerformanceBottleneck]:
        """Detect potential performance bottlenecks"""
        bottlenecks = []
        
        # Count incoming connections for each service
        incoming_connections = defaultdict(int)
        for dep in dependencies:
            if not dep.target_service.startswith('topic:'):
                incoming_connections[dep.target_service] += 1
        
        # Services with many incoming connections might be bottlenecks
        for service, count in incoming_connections.items():
            if count >= 5:  # Threshold for high connectivity
                bottlenecks.append(PerformanceBottleneck(
                    service_name=service,
                    bottleneck_type="high_traffic",
                    description=f"Service has {count} incoming dependencies, potential bottleneck",
                    severity="high" if count >= 10 else "medium"
                ))
        
        # Detect sync call chains (potential latency issues)
        sync_deps = [d for d in dependencies if d.dependency_type == "sync"]
        
        # Build outgoing sync call counts
        outgoing_sync = defaultdict(int)
        for dep in sync_deps:
            outgoing_sync[dep.source_service] += 1
        
        for service, count in outgoing_sync.items():
            if count >= 5:
                bottlenecks.append(PerformanceBottleneck(
                    service_name=service,
                    bottleneck_type="sync_chain",
                    description=f"Service makes {count} synchronous calls, potential latency accumulation",
                    severity="medium"
                ))
        
        return bottlenecks
    
    def build_topology(self, all_dependencies: List[ServiceDependency]) -> SystemTopology:
        """Build complete system topology"""
        # Extract unique services
        services = set()
        for dep in all_dependencies:
            services.add(dep.source_service)
            if not dep.target_service.startswith('topic:'):
                services.add(dep.target_service)
        
        # Detect issues
        circular_deps = self.detect_circular_dependencies(all_dependencies)
        bottlenecks = self.detect_bottlenecks(all_dependencies)
        
        return SystemTopology(
            services=sorted(list(services)),
            dependencies=all_dependencies,
            circular_dependencies=circular_deps,
            bottlenecks=bottlenecks
        )
