"""
Test script for architecture audit functionality
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.architecture.audit_service import ArchitectureAuditService


def test_local_repository():
    """Test analyzing the current repository"""
    print("🔍 Testing Architecture Audit Service\n")
    
    # Initialize service
    service = ArchitectureAuditService()
    
    # Analyze current repository
    current_repo = "/home/runner/work/Argus-IIoT/Argus-IIoT"
    print(f"📂 Analyzing repository: {current_repo}\n")
    
    try:
        report = service.audit_repositories(
            repo_urls=[],
            local_paths=[current_repo]
        )
        
        print("✅ Analysis Complete!\n")
        print(f"📊 Summary:")
        print(f"  - Total Repositories: {report.total_repositories}")
        print(f"  - Total Services: {report.total_services}")
        print(f"  - Total Endpoints: {report.api_report.total_endpoints}")
        print(f"  - Circular Dependencies: {len(report.topology.circular_dependencies)}")
        print(f"  - Performance Bottlenecks: {len(report.topology.bottlenecks)}")
        print(f"  - Breaking Changes: {len(report.api_report.breaking_changes)}")
        print(f"  - Tech Stack Items: {len(report.tech_stack_report.tech_items)}")
        print(f"  - Version Conflicts: {len(report.tech_stack_report.version_conflicts)}")
        
        # Show detected patterns
        print(f"\n🏛️ Detected Architecture Patterns:")
        for repo in report.repositories:
            print(f"  {repo.repo_name}:")
            for pattern in repo.architecture_patterns:
                pattern_name = pattern.value if hasattr(pattern, 'value') else str(pattern)
                confidence = repo.pattern_confidence.get(pattern_name, 0)
                print(f"    - {pattern_name} (confidence: {confidence:.2f})")
        
        # Show detected APIs
        if report.api_report.total_endpoints > 0:
            print(f"\n🔌 Detected API Endpoints:")
            for repo in report.repositories[:1]:  # Show first repo only
                for endpoint in repo.api_endpoints[:5]:  # Show first 5
                    api_type = endpoint.api_type.value if hasattr(endpoint.api_type, 'value') else str(endpoint.api_type)
                    print(f"    - {endpoint.method} {endpoint.path} ({api_type})")
                if len(repo.api_endpoints) > 5:
                    print(f"    ... and {len(repo.api_endpoints) - 5} more")
        
        # Show tech stack
        if report.tech_stack_report.tech_items:
            print(f"\n🛠️ Technology Stack (top 10):")
            for tech in report.tech_stack_report.tech_items[:10]:
                category = tech.category.value if hasattr(tech.category, 'value') else str(tech.category)
                print(f"    - {tech.name} {tech.version or ''} ({category})")
        
        # Generate reports
        print(f"\n📄 Generating Reports...")
        html_report = service.generate_html_report(report)
        print(f"  ✅ HTML report generated ({len(html_report)} bytes)")
        
        topology_svg = service.generate_topology_svg(report.topology)
        print(f"  ✅ Topology SVG generated ({len(topology_svg)} bytes)")
        
        pattern_svg = service.generate_pattern_distribution_svg(report)
        print(f"  ✅ Pattern distribution SVG generated ({len(pattern_svg)} bytes)")
        
        print(f"\n✨ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        service.cleanup()


if __name__ == "__main__":
    test_local_repository()
