"""
Architecture Pattern Analyzer
Identifies architecture patterns in codebases (MVC, Hexagonal, Clean Architecture, DDD, etc.)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ArchitecturePattern:
    """Architecture pattern detection result"""
    name: str
    confidence: float  # 0.0 to 1.0
    indicators: List[str] = field(default_factory=list)
    file_evidence: List[str] = field(default_factory=list)


@dataclass
class CodeStructure:
    """Code structure analysis result"""
    total_files: int = 0
    python_files: int = 0
    javascript_files: int = 0
    go_files: int = 0
    java_files: int = 0
    directories: List[str] = field(default_factory=list)
    key_patterns: Dict[str, List[str]] = field(default_factory=dict)


class ArchitectureAnalyzer:
    """Analyzes code structure to identify architecture patterns"""
    
    def __init__(self):
        self.patterns = {
            "MVC": {
                "indicators": ["models", "views", "controllers"],
                "file_patterns": [r".*controller\.py$", r".*view\.py$", r".*model\.py$"]
            },
            "Clean Architecture": {
                "indicators": ["entities", "use_cases", "interface_adapters", "frameworks"],
                "file_patterns": [r".*entity\.py$", r".*use_case\.py$", r".*repository\.py$", r".*gateway\.py$"]
            },
            "Hexagonal": {
                "indicators": ["domain", "application", "infrastructure", "ports", "adapters"],
                "file_patterns": [r".*port\.py$", r".*adapter\.py$", r"domain/.*\.py$"]
            },
            "DDD": {
                "indicators": ["domain", "aggregate", "entity", "value_object", "repository", "service"],
                "file_patterns": [r".*aggregate\.py$", r".*entity\.py$", r".*value_object\.py$", r".*domain_service\.py$"]
            },
            "Layered": {
                "indicators": ["presentation", "business", "data", "service"],
                "file_patterns": [r".*service\.py$", r".*repository\.py$", r".*controller\.py$"]
            },
            "Microservices": {
                "indicators": ["services", "api", "gateway", "discovery"],
                "file_patterns": [r".*service\.py$", r".*client\.py$", r"docker-compose\.ya?ml$"]
            }
        }
    
    def analyze_directory(self, directory_path: str) -> Dict:
        """Analyze a directory to identify architecture patterns"""
        path = Path(directory_path)
        
        if not path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        # Collect code structure information
        structure = self._analyze_structure(path)
        
        # Detect architecture patterns
        detected_patterns = self._detect_patterns(path, structure)
        
        # Identify key architectural components
        components = self._identify_components(path)
        
        return {
            "directory": str(path),
            "structure": {
                "total_files": structure.total_files,
                "python_files": structure.python_files,
                "javascript_files": structure.javascript_files,
                "go_files": structure.go_files,
                "java_files": structure.java_files,
                "directories": structure.directories,
                "key_patterns": structure.key_patterns
            },
            "detected_patterns": [
                {
                    "name": p.name,
                    "confidence": p.confidence,
                    "indicators": p.indicators,
                    "evidence": p.file_evidence[:10]  # Limit to 10 examples
                }
                for p in detected_patterns
            ],
            "components": components
        }
    
    def _analyze_structure(self, path: Path) -> CodeStructure:
        """Analyze code structure of the directory"""
        structure = CodeStructure()
        
        for root, dirs, files in os.walk(path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', '.venv', 'dist', 'build']]
            
            for dir_name in dirs:
                structure.directories.append(os.path.relpath(os.path.join(root, dir_name), path))
            
            for file in files:
                structure.total_files += 1
                
                if file.endswith('.py'):
                    structure.python_files += 1
                elif file.endswith(('.js', '.jsx', '.ts', '.tsx', '.vue')):
                    structure.javascript_files += 1
                elif file.endswith('.go'):
                    structure.go_files += 1
                elif file.endswith('.java'):
                    structure.java_files += 1
                
                # Track file patterns
                rel_path = os.path.relpath(os.path.join(root, file), path)
                for pattern_type in ["models", "views", "controllers", "services", "routes", "api", "domain", "repository"]:
                    if pattern_type in rel_path.lower():
                        if pattern_type not in structure.key_patterns:
                            structure.key_patterns[pattern_type] = []
                        structure.key_patterns[pattern_type].append(rel_path)
        
        return structure
    
    def _detect_patterns(self, path: Path, structure: CodeStructure) -> List[ArchitecturePattern]:
        """Detect architecture patterns based on code structure"""
        detected = []
        
        for pattern_name, pattern_config in self.patterns.items():
            indicators_found = []
            file_evidence = []
            
            # Check for directory indicators
            for indicator in pattern_config["indicators"]:
                for directory in structure.directories:
                    if indicator.lower() in directory.lower():
                        indicators_found.append(f"Directory: {directory}")
                        break
            
            # Check for file pattern matches
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', '.venv']]
                
                for file in files:
                    file_path = os.path.relpath(os.path.join(root, file), path)
                    for file_pattern in pattern_config["file_patterns"]:
                        if re.match(file_pattern, file_path, re.IGNORECASE):
                            file_evidence.append(file_path)
                            break
            
            # Calculate confidence score
            indicator_score = len(indicators_found) / len(pattern_config["indicators"])
            file_score = min(len(file_evidence) / 5, 1.0)  # Max at 5 matching files
            confidence = (indicator_score * 0.6 + file_score * 0.4)
            
            if confidence > 0.2:  # Only include if some evidence found
                detected.append(ArchitecturePattern(
                    name=pattern_name,
                    confidence=round(confidence, 2),
                    indicators=indicators_found,
                    file_evidence=file_evidence
                ))
        
        # Sort by confidence
        detected.sort(key=lambda x: x.confidence, reverse=True)
        
        return detected
    
    def _identify_components(self, path: Path) -> Dict[str, List[str]]:
        """Identify key architectural components"""
        components = {
            "api_endpoints": [],
            "data_models": [],
            "services": [],
            "configurations": [],
            "tests": []
        }
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', '.venv']]
            
            for file in files:
                file_path = os.path.relpath(os.path.join(root, file), path)
                
                # API endpoints
                if any(keyword in file.lower() for keyword in ['route', 'endpoint', 'api', 'handler']):
                    components["api_endpoints"].append(file_path)
                
                # Data models
                if any(keyword in file.lower() for keyword in ['model', 'schema', 'entity']):
                    components["data_models"].append(file_path)
                
                # Services
                if 'service' in file.lower():
                    components["services"].append(file_path)
                
                # Configurations
                if any(file.lower().endswith(ext) for ext in ['.yaml', '.yml', '.json', '.toml', '.ini', '.env', '.conf']):
                    components["configurations"].append(file_path)
                
                # Tests
                if any(keyword in file.lower() for keyword in ['test', 'spec']):
                    components["tests"].append(file_path)
        
        return components


# Singleton instance
architecture_analyzer = ArchitectureAnalyzer()
