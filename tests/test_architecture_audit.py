#!/usr/bin/env python3
"""
Test script for Architecture Audit Tool
Demonstrates the functionality with the current repository
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.audit_service import audit_service


def test_single_scan():
    """Test scanning a single repository"""
    print("=" * 80)
    print("TEST 1: Scanning Backend Directory")
    print("=" * 80)
    
    backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
    backend_path = os.path.abspath(backend_path)
    
    print(f"\nScanning: {backend_path}")
    
    try:
        # Perform scan
        audit_id = audit_service.scan_repository(backend_path)
        result = audit_service.get_audit_result(audit_id)
        
        print(f"\n✅ Scan completed successfully!")
        print(f"Audit ID: {audit_id}")
        print(f"Status: {result['status']}")
        
        # Display architecture patterns
        print("\n📐 Architecture Patterns Detected:")
        patterns = result['architecture']['detected_patterns']
        if patterns:
            for pattern in patterns:
                print(f"  • {pattern['name']}: {pattern['confidence'] * 100:.0f}% confidence")
                print(f"    Indicators: {', '.join(pattern['indicators'][:3])}")
        else:
            print("  No patterns detected")
        
        # Display API summary
        print("\n🔌 API Analysis:")
        api_summary = result['api']['summary']
        print(f"  • Total endpoints: {api_summary['total_endpoints']}")
        print(f"  • API types: {', '.join(api_summary['api_types']) if api_summary['api_types'] else 'None'}")
        print(f"  • Frameworks: {', '.join(api_summary['frameworks_detected']) if api_summary['frameworks_detected'] else 'None'}")
        
        # Display technology stack
        print("\n🛠️ Technology Stack:")
        tech = result['tech_stack']['technology_stack']
        print(f"  • Databases: {', '.join(tech['databases']) if tech['databases'] else 'None'}")
        print(f"  • Web Frameworks: {', '.join(tech['web_frameworks']) if tech['web_frameworks'] else 'None'}")
        print(f"  • Languages: {', '.join(tech['languages'].keys()) if tech['languages'] else 'None'}")
        print(f"  • Containerization: {', '.join(tech['containerization']) if tech['containerization'] else 'None'}")
        print(f"  • CI/CD: {', '.join(tech['ci_cd']) if tech['ci_cd'] else 'None'}")
        
        # Display recommendations
        print("\n💡 Recommendations:")
        recommendations = result['tech_stack']['recommendations']
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  No recommendations at this time")
        
        return audit_id
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_html_report(audit_id):
    """Test HTML report generation"""
    print("\n" + "=" * 80)
    print("TEST 2: Generating HTML Report")
    print("=" * 80)
    
    if not audit_id:
        print("❌ Skipping: No valid audit ID")
        return
    
    try:
        html = audit_service.generate_html_report(audit_id)
        
        # Save to file
        output_path = os.path.join('/tmp', f'audit_report_{audit_id}.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ HTML report generated successfully!")
        print(f"Report size: {len(html):,} characters")
        print(f"Saved to: {output_path}")
        print(f"\nYou can open this file in a browser to view the interactive report:")
        print(f"  file://{output_path}")
        
    except Exception as e:
        print(f"\n❌ Error generating HTML report: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_scans():
    """Test scanning multiple directories"""
    print("\n" + "=" * 80)
    print("TEST 3: Scanning Multiple Directories")
    print("=" * 80)
    
    base_path = os.path.join(os.path.dirname(__file__), '..')
    base_path = os.path.abspath(base_path)
    
    directories = [
        os.path.join(base_path, 'backend'),
        os.path.join(base_path, 'frontend'),
    ]
    
    print(f"\nScanning {len(directories)} directories:")
    for d in directories:
        print(f"  • {d}")
    
    try:
        results = audit_service.scan_multiple_repositories(directories)
        
        print(f"\n✅ Multi-scan completed!")
        print(f"Scanned: {results['scanned_repositories']}")
        print(f"Successful: {results['successful_scans']}")
        print(f"Failed: {results['failed_scans']}")
        
        # Display comparative analysis
        if 'comparative_analysis' in results:
            comp = results['comparative_analysis']
            
            print("\n📊 Comparative Analysis:")
            
            if 'architecture_patterns' in comp:
                print("\n  Architecture Patterns Across Services:")
                for pattern_name, data in comp['architecture_patterns'].items():
                    print(f"    • {pattern_name}: used in {data['count']} service(s) " +
                          f"(avg confidence: {data['avg_confidence']})")
            
            if 'technology_stack_comparison' in comp:
                tech_comp = comp['technology_stack_comparison']
                print("\n  Technology Stack Standardization:")
                print(f"    • Overall score: {tech_comp.get('overall_standardization', 0):.2f}")
                print(f"    • Databases: {tech_comp.get('databases', {}).get('count', 0)} unique")
                print(f"    • Languages: {', '.join(tech_comp.get('languages', {}).get('list', []))}")
            
            if 'standardization_recommendations' in comp:
                print("\n  Standardization Recommendations:")
                for i, rec in enumerate(comp['standardization_recommendations'], 1):
                    print(f"    {i}. {rec}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_list_audits():
    """Test listing all audits"""
    print("\n" + "=" * 80)
    print("TEST 4: Listing All Audits")
    print("=" * 80)
    
    audits = audit_service.list_audits()
    
    print(f"\nTotal audits: {len(audits)}")
    
    if audits:
        print("\nRecent audits:")
        for audit in audits[-5:]:  # Show last 5
            print(f"  • {audit['id']} - {audit['directory']} ({audit['status']})")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("Architecture Audit Tool - Test Suite")
    print("=" * 80)
    
    # Test 1: Single scan
    audit_id = test_single_scan()
    
    # Test 2: HTML report generation
    if audit_id:
        test_html_report(audit_id)
    
    # Test 3: Multiple scans
    test_multiple_scans()
    
    # Test 4: List audits
    test_list_audits()
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)
    print("\nTo use the API:")
    print("  1. Start the backend: cd backend && uvicorn app.main:app --reload")
    print("  2. Visit http://localhost:8000/docs for API documentation")
    print("  3. Start the frontend: cd frontend && npm run dev")
    print("  4. Visit http://localhost:5173/audit for the web interface")
    print()


if __name__ == "__main__":
    main()
