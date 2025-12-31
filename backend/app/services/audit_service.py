"""
Architecture Audit Service
Orchestrates the complete architecture audit process
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from app.services.architecture_analyzer import architecture_analyzer
from app.services.api_analyzer import api_analyzer
from app.services.tech_stack_auditor import tech_stack_auditor
from app.services.report_generator import html_report_generator


class AuditService:
    """Main service for orchestrating architecture audits"""
    
    def __init__(self):
        self.audits = {}  # Store audit results in memory
    
    def scan_repository(self, directory_path: str) -> str:
        """
        Scan a repository and generate comprehensive audit report
        
        Args:
            directory_path: Path to the repository to scan
            
        Returns:
            audit_id: Unique identifier for this audit
        """
        # Generate unique audit ID
        audit_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Validate directory
            if not Path(directory_path).exists():
                raise ValueError(f"Directory does not exist: {directory_path}")
            
            # Perform analyses
            architecture_data = architecture_analyzer.analyze_directory(directory_path)
            api_data = api_analyzer.analyze_directory(directory_path)
            tech_stack_data = tech_stack_auditor.analyze_directory(directory_path)
            
            # Generate API consistency report
            if api_data.get('api_contracts'):
                consistency_report = api_analyzer.generate_consistency_report(
                    api_data['api_contracts']
                )
                api_data['consistency_report'] = consistency_report
            
            # Store audit results
            self.audits[audit_id] = {
                "id": audit_id,
                "directory": directory_path,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "architecture": architecture_data,
                "api": api_data,
                "tech_stack": tech_stack_data
            }
            
            return audit_id
            
        except Exception as e:
            # Store error information
            self.audits[audit_id] = {
                "id": audit_id,
                "directory": directory_path,
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }
            raise
    
    def get_audit_result(self, audit_id: str) -> Optional[Dict]:
        """Get audit result by ID"""
        return self.audits.get(audit_id)
    
    def generate_html_report(self, audit_id: str) -> str:
        """
        Generate HTML report for an audit
        
        Args:
            audit_id: The audit ID
            
        Returns:
            HTML report as string
        """
        audit = self.audits.get(audit_id)
        
        if not audit:
            raise ValueError(f"Audit not found: {audit_id}")
        
        if audit.get('status') != 'completed':
            raise ValueError(f"Audit not completed: {audit_id}")
        
        # Generate HTML report
        html = html_report_generator.generate_report(
            architecture_data=audit['architecture'],
            api_data=audit['api'],
            tech_stack_data=audit['tech_stack'],
            topology_data=None  # Can be extended to include topology
        )
        
        return html
    
    def scan_multiple_repositories(self, directories: List[str]) -> Dict:
        """
        Scan multiple repositories and generate comparative analysis
        
        Args:
            directories: List of directory paths to scan
            
        Returns:
            Comparative analysis results
        """
        results = []
        
        for directory in directories:
            try:
                audit_id = self.scan_repository(directory)
                audit = self.audits[audit_id]
                results.append(audit)
            except Exception as e:
                results.append({
                    "directory": directory,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Generate comparative analysis
        comparative = self._generate_comparative_analysis(results)
        
        return {
            "scanned_repositories": len(directories),
            "successful_scans": len([r for r in results if r.get('status') == 'completed']),
            "failed_scans": len([r for r in results if r.get('status') == 'failed']),
            "results": results,
            "comparative_analysis": comparative
        }
    
    def _generate_comparative_analysis(self, results: List[Dict]) -> Dict:
        """Generate comparative analysis across multiple repositories"""
        successful_results = [r for r in results if r.get('status') == 'completed']
        
        if not successful_results:
            return {}
        
        # Compare architecture patterns
        all_patterns = {}
        for result in successful_results:
            patterns = result.get('architecture', {}).get('detected_patterns', [])
            for pattern in patterns:
                name = pattern['name']
                if name not in all_patterns:
                    all_patterns[name] = {
                        "count": 0,
                        "avg_confidence": 0,
                        "repositories": []
                    }
                all_patterns[name]["count"] += 1
                all_patterns[name]["avg_confidence"] += pattern['confidence']
                all_patterns[name]["repositories"].append(result['directory'])
        
        # Calculate averages
        for pattern_name, data in all_patterns.items():
            data["avg_confidence"] = round(data["avg_confidence"] / data["count"], 2)
        
        # Compare technology stacks
        tech_stacks = [r.get('tech_stack', {}) for r in successful_results]
        tech_comparison = tech_stack_auditor.compare_stacks(tech_stacks)
        
        # Count total API endpoints
        total_endpoints = sum(
            r.get('api', {}).get('summary', {}).get('total_endpoints', 0)
            for r in successful_results
        )
        
        return {
            "architecture_patterns": all_patterns,
            "technology_stack_comparison": tech_comparison,
            "total_api_endpoints": total_endpoints,
            "standardization_recommendations": self._generate_standardization_recommendations(
                all_patterns, tech_comparison
            )
        }
    
    def _generate_standardization_recommendations(
        self, patterns: Dict, tech_comparison: Dict
    ) -> List[str]:
        """Generate recommendations for standardization across services"""
        recommendations = []
        
        # Architecture pattern recommendations
        if len(patterns) > 3:
            most_common = max(patterns.items(), key=lambda x: x[1]['count'])
            recommendations.append(
                f"Consider standardizing on {most_common[0]} architecture pattern, "
                f"which is already used in {most_common[1]['count']} repositories."
            )
        
        # Technology stack recommendations
        overall_score = tech_comparison.get('overall_standardization', 0)
        if overall_score < 0.5:
            recommendations.append(
                "Technology stack shows high diversity. Consider creating a "
                "technology radar or approved technology list to improve standardization."
            )
        
        # Database recommendations
        db_count = tech_comparison.get('databases', {}).get('count', 0)
        if db_count > 3:
            recommendations.append(
                f"Detected {db_count} different database technologies. "
                "Consider consolidating to 2-3 standardized options."
            )
        
        return recommendations
    
    def list_audits(self) -> List[Dict]:
        """List all audits"""
        return [
            {
                "id": audit_id,
                "directory": audit.get("directory"),
                "timestamp": audit.get("timestamp"),
                "status": audit.get("status")
            }
            for audit_id, audit in self.audits.items()
        ]


# Singleton instance
audit_service = AuditService()
