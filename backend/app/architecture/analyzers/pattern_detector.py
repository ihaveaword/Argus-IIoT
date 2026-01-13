"""
Architecture Pattern Detector
Analyzes code structure to identify architecture patterns
"""
import os
import re
from typing import Dict, List, Tuple
from pathlib import Path

from app.architecture.models.architecture_models import ArchitecturePattern


class PatternDetector:
    """Detects architecture patterns in code repositories"""
    
    def __init__(self):
        self.pattern_indicators = {
            ArchitecturePattern.MVC: {
                'directories': ['models', 'views', 'controllers'],
                'files': ['model', 'view', 'controller'],
                'keywords': ['ModelAndView', 'ViewController', '@Controller', '@Model']
            },
            ArchitecturePattern.HEXAGONAL: {
                'directories': ['domain', 'application', 'infrastructure', 'adapters', 'ports'],
                'files': ['port', 'adapter', 'repository'],
                'keywords': ['Port', 'Adapter', 'DomainService', 'UseCase']
            },
            ArchitecturePattern.CLEAN_ARCHITECTURE: {
                'directories': ['entities', 'usecases', 'interfaces', 'frameworks'],
                'files': ['entity', 'usecase', 'interactor', 'presenter'],
                'keywords': ['UseCase', 'Entity', 'Presenter', 'Interactor', 'Gateway']
            },
            ArchitecturePattern.DDD: {
                'directories': ['domain', 'aggregate', 'valueobject', 'repository'],
                'files': ['aggregate', 'entity', 'valueobject', 'repository', 'domainservice'],
                'keywords': ['Aggregate', 'ValueObject', 'DomainEvent', 'Repository', 'Entity']
            },
            ArchitecturePattern.LAYERED: {
                'directories': ['presentation', 'business', 'data', 'service'],
                'files': ['service', 'dao', 'dto'],
                'keywords': ['Service', 'DAO', 'DTO', 'BusinessLogic']
            },
            ArchitecturePattern.EVENT_DRIVEN: {
                'directories': ['events', 'handlers', 'subscribers', 'publishers'],
                'files': ['event', 'handler', 'subscriber', 'publisher'],
                'keywords': ['EventHandler', 'EventSubscriber', 'EventPublisher', '@EventListener']
            }
        }
    
    def analyze_directory_structure(self, repo_path: str) -> Dict[ArchitecturePattern, float]:
        """
        Analyze directory structure to detect patterns
        Returns a confidence score for each pattern
        """
        if not os.path.exists(repo_path):
            return {ArchitecturePattern.UNKNOWN: 1.0}
        
        # Collect all directories and files
        all_dirs = set()
        all_files = set()
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common non-architecture directories
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '__pycache__', '.git', 'dist', 'build']]
            
            for dir_name in dirs:
                all_dirs.add(dir_name.lower())
            
            for file_name in files:
                all_files.add(file_name.lower())
        
        # Calculate confidence scores
        pattern_scores = {}
        
        for pattern, indicators in self.pattern_indicators.items():
            score = 0.0
            total_checks = 0
            
            # Check directories
            for dir_indicator in indicators['directories']:
                total_checks += 1
                if dir_indicator.lower() in all_dirs:
                    score += 1.0
            
            # Check file naming patterns
            for file_indicator in indicators['files']:
                total_checks += 1
                for file_name in all_files:
                    if file_indicator.lower() in file_name:
                        score += 0.5
                        break
            
            # Normalize score
            if total_checks > 0:
                pattern_scores[pattern] = min(score / total_checks, 1.0)
            else:
                pattern_scores[pattern] = 0.0
        
        # If no pattern detected with confidence > 0.3, mark as unknown
        if all(score < 0.3 for score in pattern_scores.values()):
            pattern_scores[ArchitecturePattern.UNKNOWN] = 1.0
        
        return pattern_scores
    
    def analyze_code_keywords(self, repo_path: str) -> Dict[ArchitecturePattern, float]:
        """
        Analyze code content for pattern-specific keywords
        """
        if not os.path.exists(repo_path):
            return {}
        
        pattern_keyword_counts = {pattern: 0 for pattern in self.pattern_indicators.keys()}
        total_files_analyzed = 0
        
        # Analyze source files
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '__pycache__', '.git']]
            
            for file_name in files:
                if not (file_name.endswith(('.py', '.java', '.js', '.ts', '.go', '.cs'))):
                    continue
                
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        total_files_analyzed += 1
                        
                        for pattern, indicators in self.pattern_indicators.items():
                            for keyword in indicators['keywords']:
                                if keyword in content:
                                    pattern_keyword_counts[pattern] += 1
                except Exception:
                    continue
        
        # Normalize scores
        pattern_scores = {}
        if total_files_analyzed > 0:
            for pattern, count in pattern_keyword_counts.items():
                pattern_scores[pattern] = min(count / (total_files_analyzed * 0.1), 1.0)
        
        return pattern_scores
    
    def detect_patterns(self, repo_path: str) -> Tuple[List[ArchitecturePattern], Dict[str, float]]:
        """
        Main method to detect architecture patterns
        Returns detected patterns and confidence scores
        """
        # Combine directory and code analysis
        dir_scores = self.analyze_directory_structure(repo_path)
        code_scores = self.analyze_code_keywords(repo_path)
        
        # Merge scores (weighted average)
        combined_scores = {}
        all_patterns = set(dir_scores.keys()) | set(code_scores.keys())
        
        for pattern in all_patterns:
            dir_score = dir_scores.get(pattern, 0.0)
            code_score = code_scores.get(pattern, 0.0)
            # Weight directory structure more heavily
            combined_scores[pattern] = (dir_score * 0.6 + code_score * 0.4)
        
        # Select patterns with confidence > 0.3
        detected_patterns = [
            pattern for pattern, score in combined_scores.items()
            if score >= 0.3 and pattern != ArchitecturePattern.UNKNOWN
        ]
        
        if not detected_patterns:
            detected_patterns = [ArchitecturePattern.UNKNOWN]
        
        # Convert to string keys for JSON serialization
        confidence_dict = {pattern.value: score for pattern, score in combined_scores.items()}
        
        return detected_patterns, confidence_dict
