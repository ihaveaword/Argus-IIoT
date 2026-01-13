"""
API Contract Analyzer
Analyzes API endpoints and detects breaking changes
"""
import os
import re
from typing import List, Dict, Set
from pathlib import Path

from app.architecture.models.architecture_models import (
    APIEndpoint, APIType, BreakingChange, APICompatibilityReport
)


class APIAnalyzer:
    """Analyzes API contracts and compatibility"""
    
    def __init__(self):
        # Patterns for detecting different API types
        self.rest_patterns = [
            r'@(Get|Post|Put|Delete|Patch)Mapping',  # Spring
            r'@app\.(get|post|put|delete|patch)',  # FastAPI/Flask
            r'router\.(get|post|put|delete|patch)',  # Express/FastAPI Router
            r'@(GET|POST|PUT|DELETE|PATCH)\s*\(',  # JAX-RS
        ]
        
        self.grpc_patterns = [
            r'service\s+\w+\s*{',  # Proto service definition
            r'rpc\s+\w+\s*\(',  # RPC method
            r'import.*grpc',
        ]
        
        self.graphql_patterns = [
            r'type\s+Query\s*{',
            r'type\s+Mutation\s*{',
            r'@Query',
            r'@Mutation',
            r'GraphQL',
        ]
    
    def detect_api_type(self, content: str) -> APIType:
        """Detect API type from file content"""
        # Check gRPC
        for pattern in self.grpc_patterns:
            if re.search(pattern, content):
                return APIType.GRPC
        
        # Check GraphQL
        for pattern in self.graphql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return APIType.GRAPHQL
        
        # Check REST
        for pattern in self.rest_patterns:
            if re.search(pattern, content):
                return APIType.REST
        
        # Check WebSocket
        if re.search(r'WebSocket|ws://|wss://', content, re.IGNORECASE):
            return APIType.WEBSOCKET
        
        return APIType.UNKNOWN
    
    def extract_rest_endpoints(self, content: str, file_path: str, service_name: str) -> List[APIEndpoint]:
        """Extract REST API endpoints from code"""
        endpoints = []
        
        # Pattern for FastAPI/Flask style
        fastapi_pattern = r'@\w+\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)'
        matches = re.finditer(fastapi_pattern, content, re.IGNORECASE)
        
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            
            endpoints.append(APIEndpoint(
                method=method,
                path=path,
                api_type=APIType.REST,
                service_name=service_name,
                file_location=file_path
            ))
        
        # Pattern for Spring style
        spring_pattern = r'@(Get|Post|Put|Delete|Patch)Mapping\(["\']([^"\']+)["\']\)'
        matches = re.finditer(spring_pattern, content)
        
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            
            endpoints.append(APIEndpoint(
                method=method,
                path=path,
                api_type=APIType.REST,
                service_name=service_name,
                file_location=file_path
            ))
        
        # Pattern for Express.js style
        express_pattern = r'router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\s*,'
        matches = re.finditer(express_pattern, content, re.IGNORECASE)
        
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            
            endpoints.append(APIEndpoint(
                method=method,
                path=path,
                api_type=APIType.REST,
                service_name=service_name,
                file_location=file_path
            ))
        
        return endpoints
    
    def extract_grpc_services(self, content: str, file_path: str, service_name: str) -> List[APIEndpoint]:
        """Extract gRPC service definitions"""
        endpoints = []
        
        # Extract RPC methods from proto files
        rpc_pattern = r'rpc\s+(\w+)\s*\(([^)]+)\)\s*returns\s*\(([^)]+)\)'
        matches = re.finditer(rpc_pattern, content)
        
        for match in matches:
            method_name = match.group(1)
            request_type = match.group(2).strip()
            response_type = match.group(3).strip()
            
            endpoints.append(APIEndpoint(
                method="RPC",
                path=method_name,
                api_type=APIType.GRPC,
                request_schema={"type": request_type},
                response_schema={"type": response_type},
                service_name=service_name,
                file_location=file_path
            ))
        
        return endpoints
    
    def extract_graphql_schema(self, content: str, file_path: str, service_name: str) -> List[APIEndpoint]:
        """Extract GraphQL queries and mutations"""
        endpoints = []
        
        # Extract queries
        query_pattern = r'type\s+Query\s*\{([^}]+)\}'
        query_match = re.search(query_pattern, content, re.DOTALL)
        if query_match:
            fields = re.findall(r'(\w+)\s*(\([^)]*\))?\s*:\s*(\w+)', query_match.group(1))
            for field in fields:
                endpoints.append(APIEndpoint(
                    method="QUERY",
                    path=field[0],
                    api_type=APIType.GRAPHQL,
                    service_name=service_name,
                    file_location=file_path
                ))
        
        # Extract mutations
        mutation_pattern = r'type\s+Mutation\s*\{([^}]+)\}'
        mutation_match = re.search(mutation_pattern, content, re.DOTALL)
        if mutation_match:
            fields = re.findall(r'(\w+)\s*(\([^)]*\))?\s*:\s*(\w+)', mutation_match.group(1))
            for field in fields:
                endpoints.append(APIEndpoint(
                    method="MUTATION",
                    path=field[0],
                    api_type=APIType.GRAPHQL,
                    service_name=service_name,
                    file_location=file_path
                ))
        
        return endpoints
    
    def analyze_repository(self, repo_path: str, service_name: str) -> List[APIEndpoint]:
        """Analyze a repository for API endpoints"""
        all_endpoints = []
        
        if not os.path.exists(repo_path):
            return all_endpoints
        
        # File extensions to analyze
        api_file_patterns = ['.py', '.java', '.js', '.ts', '.go', '.proto', '.graphql', '.gql']
        
        for root, dirs, files in os.walk(repo_path):
            # Skip non-source directories
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '__pycache__', '.git', 'dist', 'build']]
            
            for file_name in files:
                if not any(file_name.endswith(ext) for ext in api_file_patterns):
                    continue
                
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, repo_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        api_type = self.detect_api_type(content)
                        
                        if api_type == APIType.REST:
                            endpoints = self.extract_rest_endpoints(content, relative_path, service_name)
                            all_endpoints.extend(endpoints)
                        elif api_type == APIType.GRPC:
                            endpoints = self.extract_grpc_services(content, relative_path, service_name)
                            all_endpoints.extend(endpoints)
                        elif api_type == APIType.GRAPHQL:
                            endpoints = self.extract_graphql_schema(content, relative_path, service_name)
                            all_endpoints.extend(endpoints)
                
                except Exception:
                    continue
        
        return all_endpoints
    
    def detect_breaking_changes(self, endpoints: List[APIEndpoint]) -> List[BreakingChange]:
        """
        Detect potential breaking changes in API contracts
        This is a simplified implementation - in production, this would compare
        with historical API versions
        """
        breaking_changes = []
        
        # Check for common breaking change patterns
        endpoint_paths = {}
        for endpoint in endpoints:
            key = f"{endpoint.method}:{endpoint.path}"
            if key not in endpoint_paths:
                endpoint_paths[key] = []
            endpoint_paths[key].append(endpoint)
        
        # Detect duplicate endpoints (potential conflicts)
        for key, eps in endpoint_paths.items():
            if len(eps) > 1:
                services = [ep.service_name for ep in eps]
                breaking_changes.append(BreakingChange(
                    endpoint=key,
                    change_type="duplicate_endpoint",
                    description=f"Duplicate endpoint definition found in multiple services",
                    affected_services=services,
                    severity="medium"
                ))
        
        return breaking_changes
    
    def generate_compatibility_report(self, all_endpoints: List[APIEndpoint]) -> APICompatibilityReport:
        """Generate API compatibility report"""
        breaking_changes = self.detect_breaking_changes(all_endpoints)
        
        # Detect API standards violations
        violations = []
        
        # Check for inconsistent REST patterns
        rest_endpoints = [ep for ep in all_endpoints if ep.api_type == APIType.REST]
        if rest_endpoints:
            # Check for non-standard HTTP methods
            for ep in rest_endpoints:
                if ep.method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    violations.append(f"Non-standard HTTP method '{ep.method}' in {ep.service_name}")
        
        return APICompatibilityReport(
            total_endpoints=len(all_endpoints),
            breaking_changes=breaking_changes,
            api_standards_violations=violations
        )
