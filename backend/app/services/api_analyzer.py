"""
API Contract Analyzer
Analyzes REST/gRPC/GraphQL APIs and generates contract consistency reports
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class APIEndpoint:
    """API endpoint information"""
    path: str
    method: str
    handler: str
    file: str
    line: int = 0
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    description: Optional[str] = None


@dataclass
class APIContract:
    """API contract information"""
    type: str  # REST, gRPC, GraphQL
    endpoints: List[APIEndpoint] = field(default_factory=list)
    version: Optional[str] = None
    base_path: Optional[str] = None


class APIAnalyzer:
    """Analyzes API contracts across services"""
    
    def __init__(self):
        self.rest_patterns = {
            "fastapi": [
                r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
            ],
            "flask": [
                r'@app\.route\(["\']([^"\']+)["\'].*methods=\[["\'](GET|POST|PUT|DELETE|PATCH)["\']',
                r'@blueprint\.route\(["\']([^"\']+)["\']'
            ],
            "express": [
                r'(app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
            ],
            "django": [
                r'path\(["\']([^"\']+)["\']'
            ]
        }
    
    def analyze_directory(self, directory_path: str) -> Dict:
        """Analyze directory for API contracts"""
        path = Path(directory_path)
        
        if not path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        contracts = self._discover_api_contracts(path)
        
        return {
            "directory": str(path),
            "api_contracts": contracts,
            "summary": {
                "total_endpoints": sum(len(c["endpoints"]) for c in contracts),
                "api_types": list(set(c["type"] for c in contracts)),
                "frameworks_detected": list(set(c.get("framework", "unknown") for c in contracts))
            }
        }
    
    def _discover_api_contracts(self, path: Path) -> List[Dict]:
        """Discover all API contracts in the directory"""
        contracts = []
        
        # Analyze Python files for FastAPI, Flask, Django
        python_endpoints = self._analyze_python_apis(path)
        if python_endpoints:
            contracts.append({
                "type": "REST",
                "framework": self._detect_python_framework(path),
                "endpoints": python_endpoints,
                "file_count": len(set(ep["file"] for ep in python_endpoints))
            })
        
        # Analyze JavaScript/TypeScript files for Express, NestJS
        js_endpoints = self._analyze_javascript_apis(path)
        if js_endpoints:
            contracts.append({
                "type": "REST",
                "framework": self._detect_js_framework(path),
                "endpoints": js_endpoints,
                "file_count": len(set(ep["file"] for ep in js_endpoints))
            })
        
        # Check for GraphQL schemas
        graphql_schemas = self._find_graphql_schemas(path)
        if graphql_schemas:
            contracts.append({
                "type": "GraphQL",
                "schemas": graphql_schemas,
                "file_count": len(graphql_schemas)
            })
        
        # Check for gRPC proto files
        grpc_protos = self._find_grpc_protos(path)
        if grpc_protos:
            contracts.append({
                "type": "gRPC",
                "proto_files": grpc_protos,
                "file_count": len(grpc_protos)
            })
        
        return contracts
    
    def _analyze_python_apis(self, path: Path) -> List[Dict]:
        """Analyze Python files for REST API endpoints"""
        endpoints = []
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', '.venv']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Try to parse as AST for more accurate analysis
                        try:
                            tree = ast.parse(content)
                            endpoints.extend(self._extract_python_endpoints_ast(tree, str(file_path.relative_to(path))))
                        except:
                            # Fallback to regex if AST parsing fails
                            endpoints.extend(self._extract_python_endpoints_regex(content, str(file_path.relative_to(path))))
                    except:
                        pass
        
        return endpoints
    
    def _extract_python_endpoints_ast(self, tree: ast.AST, file_path: str) -> List[Dict]:
        """Extract API endpoints using AST parsing"""
        endpoints = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if hasattr(decorator.func, 'attr'):
                            method = decorator.func.attr
                            if method in ['get', 'post', 'put', 'delete', 'patch']:
                                # Extract path from first argument
                                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                    path = decorator.args[0].value
                                    
                                    # Extract parameters
                                    params = [arg.arg for arg in node.args.args if arg.arg != 'self']
                                    
                                    # Extract docstring
                                    docstring = ast.get_docstring(node)
                                    
                                    endpoints.append({
                                        "path": path,
                                        "method": method.upper(),
                                        "handler": node.name,
                                        "file": file_path,
                                        "line": node.lineno,
                                        "parameters": params,
                                        "description": docstring.split('\n')[0] if docstring else None
                                    })
        
        return endpoints
    
    def _extract_python_endpoints_regex(self, content: str, file_path: str) -> List[Dict]:
        """Extract API endpoints using regex patterns"""
        endpoints = []
        
        for framework, patterns in self.rest_patterns.items():
            if framework in ['fastapi', 'flask', 'django']:
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        if framework == 'fastapi':
                            method = match.group(1).upper()
                            path = match.group(2)
                        elif framework == 'flask':
                            path = match.group(1)
                            method = match.group(2) if match.lastindex >= 2 else 'GET'
                        else:
                            continue
                        
                        endpoints.append({
                            "path": path,
                            "method": method,
                            "file": file_path,
                            "framework": framework
                        })
        
        return endpoints
    
    def _analyze_javascript_apis(self, path: Path) -> List[Dict]:
        """Analyze JavaScript/TypeScript files for REST API endpoints"""
        endpoints = []
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', '.venv']]
            
            for file in files:
                if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Use regex patterns for Express-style APIs
                        for pattern in self.rest_patterns.get('express', []):
                            matches = re.finditer(pattern, content, re.MULTILINE)
                            for match in matches:
                                method = match.group(2).upper() if match.lastindex >= 2 else 'GET'
                                path = match.group(3) if match.lastindex >= 3 else match.group(1)
                                
                                endpoints.append({
                                    "path": path,
                                    "method": method,
                                    "file": str(file_path.relative_to(path)),
                                    "framework": "express"
                                })
                    except:
                        pass
        
        return endpoints
    
    def _find_graphql_schemas(self, path: Path) -> List[str]:
        """Find GraphQL schema files"""
        schemas = []
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', '.venv']]
            
            for file in files:
                if file.endswith(('.graphql', '.gql')) or 'schema' in file.lower():
                    file_path = Path(root) / file
                    schemas.append(str(file_path.relative_to(path)))
        
        return schemas
    
    def _find_grpc_protos(self, path: Path) -> List[str]:
        """Find gRPC proto files"""
        protos = []
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', '.venv']]
            
            for file in files:
                if file.endswith('.proto'):
                    file_path = Path(root) / file
                    protos.append(str(file_path.relative_to(path)))
        
        return protos
    
    def _detect_python_framework(self, path: Path) -> str:
        """Detect Python web framework used"""
        requirements_file = path / "requirements.txt"
        
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    content = f.read().lower()
                    if 'fastapi' in content:
                        return 'FastAPI'
                    elif 'flask' in content:
                        return 'Flask'
                    elif 'django' in content:
                        return 'Django'
            except:
                pass
        
        return 'unknown'
    
    def _detect_js_framework(self, path: Path) -> str:
        """Detect JavaScript framework used"""
        package_file = path / "package.json"
        
        if package_file.exists():
            try:
                import json
                with open(package_file, 'r') as f:
                    data = json.load(f)
                    dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    if 'express' in dependencies:
                        return 'Express'
                    elif '@nestjs/core' in dependencies:
                        return 'NestJS'
                    elif 'koa' in dependencies:
                        return 'Koa'
            except:
                pass
        
        return 'unknown'
    
    def generate_consistency_report(self, contracts: List[Dict]) -> Dict:
        """Generate API contract consistency report"""
        # Analyze endpoint patterns
        all_endpoints = []
        for contract in contracts:
            if 'endpoints' in contract:
                all_endpoints.extend(contract['endpoints'])
        
        # Find potential inconsistencies
        inconsistencies = []
        
        # Check for similar paths with different methods
        path_methods = {}
        for ep in all_endpoints:
            path = ep['path']
            method = ep['method']
            if path not in path_methods:
                path_methods[path] = set()
            path_methods[path].add(method)
        
        # Check naming conventions
        naming_issues = []
        for ep in all_endpoints:
            path = ep['path']
            # Check for inconsistent naming (snake_case vs camelCase vs kebab-case)
            if '_' in path and '-' in path:
                naming_issues.append({
                    "path": path,
                    "issue": "Mixed naming conventions (underscore and hyphen)",
                    "file": ep.get('file', 'unknown')
                })
        
        return {
            "total_endpoints": len(all_endpoints),
            "unique_paths": len(path_methods),
            "methods_distribution": self._count_methods(all_endpoints),
            "naming_inconsistencies": naming_issues[:10],  # Limit to 10 examples
            "recommendations": self._generate_recommendations(all_endpoints, naming_issues)
        }
    
    def _count_methods(self, endpoints: List[Dict]) -> Dict[str, int]:
        """Count HTTP methods used"""
        methods = {}
        for ep in endpoints:
            method = ep.get('method', 'UNKNOWN')
            methods[method] = methods.get(method, 0) + 1
        return methods
    
    def _generate_recommendations(self, endpoints: List[Dict], naming_issues: List[Dict]) -> List[str]:
        """Generate consistency recommendations"""
        recommendations = []
        
        if naming_issues:
            recommendations.append("Standardize path naming conventions across all services")
        
        # Check if versioning is used
        versioned = sum(1 for ep in endpoints if re.search(r'/v\d+/', ep['path']))
        if versioned < len(endpoints) * 0.5:
            recommendations.append("Consider implementing API versioning (e.g., /v1/) for all endpoints")
        
        return recommendations


# Singleton instance
api_analyzer = APIAnalyzer()
