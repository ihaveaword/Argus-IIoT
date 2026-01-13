"""
Architecture Audit Service
Main orchestrator for architecture analysis
"""
import os
from typing import List, Optional
from datetime import datetime

from app.architecture.models.architecture_models import (
    ArchitectureAuditReport, SystemTopology, APICompatibilityReport, TechStackReport
)
from app.architecture.utils.github_scanner import GitHubScanner
from app.architecture.analyzers.topology_analyzer import TopologyAnalyzer
from app.architecture.analyzers.api_analyzer import APIAnalyzer
from app.architecture.analyzers.tech_stack_analyzer import TechStackAnalyzer
from app.architecture.generators.html_report_generator import HTMLReportGenerator
from app.architecture.generators.svg_diagram_generator import SVGDiagramGenerator


class ArchitectureAuditService:
    """Main service for architecture auditing"""
    
    def __init__(self):
        self.scanner = GitHubScanner()
        self.topology_analyzer = TopologyAnalyzer()
        self.api_analyzer = APIAnalyzer()
        self.tech_stack_analyzer = TechStackAnalyzer()
        self.html_generator = HTMLReportGenerator()
        self.svg_generator = SVGDiagramGenerator()
    
    def audit_repositories(self, repo_urls: List[str], 
                          local_paths: Optional[List[str]] = None) -> ArchitectureAuditReport:
        """
        Audit multiple repositories
        
        Args:
            repo_urls: List of GitHub repository URLs to clone and analyze
            local_paths: Optional list of local repository paths (already cloned)
        
        Returns:
            Complete architecture audit report
        """
        repositories = []
        all_dependencies = []
        all_endpoints = []
        all_tech_items = []
        
        # Analyze remote repositories
        if repo_urls:
            for repo_url in repo_urls:
                print(f"Scanning repository: {repo_url}")
                repo_analysis = self.scanner.scan_repository(repo_url)
                
                if repo_analysis:
                    repositories.append(repo_analysis)
                    all_endpoints.extend(repo_analysis.api_endpoints)
                    all_tech_items.extend(repo_analysis.tech_stack)
                    
                    # Extract dependencies for each service
                    for service in repo_analysis.services:
                        repo_path = os.path.join(self.scanner.temp_dir, repo_analysis.repo_name)
                        service_path = os.path.join(repo_path, service) if service != repo_analysis.repo_name else repo_path
                        if os.path.exists(service_path):
                            deps = self.topology_analyzer.analyze_repository(service_path, service)
                            all_dependencies.extend(deps)
        
        # Analyze local repositories
        if local_paths:
            for local_path in local_paths:
                if os.path.exists(local_path):
                    repo_name = os.path.basename(local_path)
                    print(f"Scanning local repository: {repo_name}")
                    repo_analysis = self.scanner.scan_local_repository(
                        local_path, repo_name, f"file://{local_path}"
                    )
                    
                    repositories.append(repo_analysis)
                    all_endpoints.extend(repo_analysis.api_endpoints)
                    all_tech_items.extend(repo_analysis.tech_stack)
                    
                    # Extract dependencies
                    for service in repo_analysis.services:
                        service_path = os.path.join(local_path, service) if service != repo_name else local_path
                        if os.path.exists(service_path):
                            deps = self.topology_analyzer.analyze_repository(service_path, service)
                            all_dependencies.extend(deps)
        
        # Build system topology
        topology = self.topology_analyzer.build_topology(all_dependencies)
        
        # Generate API compatibility report
        api_report = self.api_analyzer.generate_compatibility_report(all_endpoints)
        
        # Generate tech stack report
        tech_stack_report = self.tech_stack_analyzer.generate_standardization_report(all_tech_items)
        
        # Count total services
        total_services = len(topology.services)
        
        # Create final report
        report = ArchitectureAuditReport(
            repositories=repositories,
            topology=topology,
            api_report=api_report,
            tech_stack_report=tech_stack_report,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_services=total_services,
            total_repositories=len(repositories)
        )
        
        return report
    
    def generate_html_report(self, report: ArchitectureAuditReport) -> str:
        """Generate interactive HTML report"""
        return self.html_generator.generate_report(report)
    
    def generate_topology_svg(self, topology: SystemTopology) -> str:
        """Generate topology SVG diagram"""
        return self.svg_generator.generate_topology_diagram(topology)
    
    def generate_pattern_distribution_svg(self, report: ArchitectureAuditReport) -> str:
        """Generate pattern distribution SVG chart"""
        # Count patterns
        pattern_counts = {}
        for repo in report.repositories:
            for pattern in repo.architecture_patterns:
                pattern_name = pattern.value if hasattr(pattern, 'value') else str(pattern)
                pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1
        
        return self.svg_generator.generate_pattern_distribution_chart(pattern_counts)
    
    def cleanup(self):
        """Clean up temporary files"""
        self.scanner.cleanup()
