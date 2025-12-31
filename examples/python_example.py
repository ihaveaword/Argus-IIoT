"""
Python example for using the Architecture Audit API
"""

import requests
import json


def main():
    base_url = "http://localhost:8000"
    
    print("=" * 80)
    print("Architecture Audit API - Python Example")
    print("=" * 80)
    print()
    
    # 1. Check API health
    print("1. Checking API health...")
    response = requests.get(f"{base_url}/api/audit/health")
    print(json.dumps(response.json(), indent=2))
    print()
    
    # 2. Scan a repository
    print("2. Scanning repository...")
    scan_request = {
        "directory_path": "/home/runner/work/Argus-IIoT/Argus-IIoT/backend"
    }
    
    response = requests.post(
        f"{base_url}/api/audit/scan",
        json=scan_request
    )
    
    scan_result = response.json()
    print(json.dumps(scan_result, indent=2))
    
    if not scan_result.get("success"):
        print("Error: Scan failed")
        return
    
    audit_id = scan_result["audit_id"]
    print()
    
    # 3. Get detailed audit results
    print(f"3. Getting detailed audit results for ID: {audit_id}")
    response = requests.get(f"{base_url}/api/audit/audit/{audit_id}")
    audit_data = response.json()
    
    # Display architecture patterns
    print("\n📐 Architecture Patterns:")
    for pattern in audit_data["architecture"]["detected_patterns"]:
        print(f"  • {pattern['name']}")
        print(f"    Confidence: {pattern['confidence'] * 100:.0f}%")
        print(f"    Evidence: {len(pattern['evidence'])} files")
    
    # Display API endpoints
    print("\n🔌 API Endpoints:")
    api_summary = audit_data["api"]["summary"]
    print(f"  Total endpoints: {api_summary['total_endpoints']}")
    print(f"  API types: {', '.join(api_summary['api_types']) if api_summary['api_types'] else 'None'}")
    
    # Display technology stack
    print("\n🛠️ Technology Stack:")
    tech = audit_data["tech_stack"]["technology_stack"]
    print(f"  Web Frameworks: {', '.join(tech['web_frameworks']) if tech['web_frameworks'] else 'None'}")
    print(f"  Languages: {', '.join(tech['languages'].keys()) if tech['languages'] else 'None'}")
    
    # Display recommendations
    print("\n💡 Recommendations:")
    for i, rec in enumerate(audit_data["tech_stack"]["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    print()
    
    # 4. Generate report URL
    report_url = f"{base_url}/api/audit/report/{audit_id}"
    print("=" * 80)
    print("✅ Audit completed!")
    print("=" * 80)
    print()
    print("View the interactive HTML report at:")
    print(f"  {report_url}")
    print()
    print("Features in the HTML report:")
    print("  • Architecture patterns with confidence scores")
    print("  • Complete API endpoint listing")
    print("  • Technology stack comparison")
    print("  • Standardization recommendations")
    print("  • Downloadable ADR template")
    print()
    
    # 5. List all audits
    print("5. Listing all audits...")
    response = requests.get(f"{base_url}/api/audit/audits")
    audits_data = response.json()
    print(f"Total audits: {audits_data['total_audits']}")
    for audit in audits_data["audits"][-3:]:  # Show last 3
        print(f"  • {audit['id']} - {audit['status']}")
    print()


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the API server")
        print("Please ensure the backend is running:")
        print("  cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
