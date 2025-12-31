"""
GitHub Repository Scanner
Scans GitHub repositories for architecture analysis
"""
import os
import subprocess
import tempfile
import shutil
from typing import List, Optional
from pathlib import Path

from app.architecture.models.architecture_models import RepositoryAnalysis
from app.architecture.analyzers.pattern_detector import PatternDetector
from app.architecture.analyzers.api_analyzer import APIAnalyzer
from app.architecture.analyzers.tech_stack_analyzer import TechStackAnalyzer


class GitHubScanner:
    """Scans GitHub repositories for analysis"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="arch_analysis_")
        self.pattern_detector = PatternDetector()
        self.api_analyzer = APIAnalyzer()
        self.tech_stack_analyzer = TechStackAnalyzer()
    
    def clone_repository(self, repo_url: str, repo_name: str) -> Optional[str]:
        """
        Clone a GitHub repository
        Returns the path to the cloned repository
        """
        repo_path = os.path.join(self.temp_dir, repo_name)
        
        # Skip if already cloned
        if os.path.exists(repo_path):
            return repo_path
        
        try:
            # Use git clone with depth 1 for faster cloning
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, repo_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return repo_path
            else:
                print(f"Failed to clone {repo_url}: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            print(f"Timeout cloning {repo_url}")
            return None
        except Exception as e:
            print(f"Error cloning {repo_url}: {str(e)}")
            return None
    
    def scan_local_repository(self, repo_path: str, repo_name: str, repo_url: str = "") -> RepositoryAnalysis:
        """
        Scan a local repository (already cloned or local path)
        """
        # Detect architecture patterns
        patterns, pattern_confidence = self.pattern_detector.detect_patterns(repo_path)
        
        # Extract services (simple heuristic: top-level directories that look like services)
        services = self._detect_services(repo_path)
        if not services:
            services = [repo_name]  # Use repo name as default service
        
        # Analyze APIs for each service
        all_endpoints = []
        for service in services:
            service_path = os.path.join(repo_path, service) if service != repo_name else repo_path
            if os.path.exists(service_path):
                endpoints = self.api_analyzer.analyze_repository(service_path, service)
                all_endpoints.extend(endpoints)
        
        # Analyze technology stack
        tech_stack = self.tech_stack_analyzer.analyze_repository(repo_path, repo_name)
        
        # Get file structure
        file_structure = self._get_file_structure(repo_path)
        
        return RepositoryAnalysis(
            repo_name=repo_name,
            repo_url=repo_url,
            architecture_patterns=patterns,
            pattern_confidence=pattern_confidence,
            api_endpoints=all_endpoints,
            tech_stack=tech_stack,
            services=services,
            file_structure=file_structure
        )
    
    def scan_repository(self, repo_url: str, repo_name: Optional[str] = None) -> Optional[RepositoryAnalysis]:
        """
        Scan a GitHub repository
        """
        if not repo_name:
            # Extract repo name from URL
            repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        
        # Clone the repository
        repo_path = self.clone_repository(repo_url, repo_name)
        
        if not repo_path:
            return None
        
        return self.scan_local_repository(repo_path, repo_name, repo_url)
    
    def _detect_services(self, repo_path: str) -> List[str]:
        """
        Detect services in a repository
        Simple heuristic: look for directories with package management files
        """
        services = []
        
        # Check if it's a monorepo with multiple services
        try:
            entries = os.listdir(repo_path)
            for entry in entries:
                entry_path = os.path.join(repo_path, entry)
                if os.path.isdir(entry_path) and not entry.startswith('.'):
                    # Check if it looks like a service
                    has_package_file = any(
                        os.path.exists(os.path.join(entry_path, f))
                        for f in ['package.json', 'requirements.txt', 'pom.xml', 'go.mod']
                    )
                    
                    # Check for source code
                    has_source = any(
                        os.path.exists(os.path.join(entry_path, d))
                        for d in ['src', 'app', 'lib', 'main.py', 'index.js']
                    )
                    
                    if has_package_file or has_source:
                        services.append(entry)
        except Exception:
            pass
        
        return services
    
    def _get_file_structure(self, repo_path: str, max_depth: int = 3) -> dict:
        """
        Get file structure of repository
        Returns a dict with directory names as keys and file lists as values
        """
        structure = {}
        
        try:
            for root, dirs, files in os.walk(repo_path):
                # Calculate depth
                depth = root[len(repo_path):].count(os.sep)
                if depth >= max_depth:
                    dirs[:] = []  # Don't recurse deeper
                    continue
                
                # Skip common non-source directories
                dirs[:] = [d for d in dirs if d not in [
                    'node_modules', 'venv', '__pycache__', '.git', 
                    'dist', 'build', 'target', 'bin', 'obj'
                ]]
                
                relative_path = os.path.relpath(root, repo_path)
                if relative_path == '.':
                    relative_path = '/'
                
                # Store files in this directory
                structure[relative_path] = [f for f in files if not f.startswith('.')]
        except Exception:
            pass
        
        return structure
    
    def cleanup(self):
        """Clean up temporary directories"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Failed to cleanup {self.temp_dir}: {str(e)}")
