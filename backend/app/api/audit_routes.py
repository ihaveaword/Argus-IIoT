"""
Architecture Audit API Routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.audit_service import audit_service

audit_router = APIRouter()


class ScanRequest(BaseModel):
    """Request model for scanning a repository"""
    directory_path: str = Field(..., description="Path to the repository directory to scan")


class MultiScanRequest(BaseModel):
    """Request model for scanning multiple repositories"""
    directories: List[str] = Field(..., description="List of repository directory paths to scan")


@audit_router.post("/scan")
async def scan_repository(request: ScanRequest):
    """
    Scan a single repository for architecture patterns, APIs, and technology stack
    
    - **directory_path**: Path to the repository to scan (e.g., /home/runner/work/Argus-IIoT/Argus-IIoT)
    """
    try:
        audit_id = audit_service.scan_repository(request.directory_path)
        audit = audit_service.get_audit_result(audit_id)
        
        return JSONResponse({
            "success": True,
            "audit_id": audit_id,
            "directory": request.directory_path,
            "timestamp": audit['timestamp'],
            "summary": {
                "architecture_patterns": len(audit['architecture']['detected_patterns']),
                "api_endpoints": audit['api']['summary']['total_endpoints'],
                "tech_stack_items": len(audit['tech_stack']['technology_stack'].get('databases', [])) +
                                   len(audit['tech_stack']['technology_stack'].get('web_frameworks', []))
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@audit_router.post("/scan-multiple")
async def scan_multiple_repositories(request: MultiScanRequest):
    """
    Scan multiple repositories and generate comparative analysis
    
    - **directories**: List of repository paths to scan
    """
    try:
        results = audit_service.scan_multiple_repositories(request.directories)
        
        return JSONResponse({
            "success": True,
            "scanned_repositories": results['scanned_repositories'],
            "successful_scans": results['successful_scans'],
            "failed_scans": results['failed_scans'],
            "comparative_analysis": results['comparative_analysis']
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-scan failed: {str(e)}")


@audit_router.get("/audit/{audit_id}")
async def get_audit_result(audit_id: str):
    """
    Get audit result by ID
    
    - **audit_id**: The unique audit identifier
    """
    audit = audit_service.get_audit_result(audit_id)
    
    if not audit:
        raise HTTPException(status_code=404, detail=f"Audit not found: {audit_id}")
    
    return JSONResponse(audit)


@audit_router.get("/report/{audit_id}", response_class=HTMLResponse)
async def get_html_report(audit_id: str):
    """
    Get interactive HTML report for an audit
    
    - **audit_id**: The unique audit identifier
    
    Returns an interactive HTML page with:
    - Architecture patterns visualization
    - API contracts analysis
    - Technology stack comparison
    - ADR template
    """
    try:
        html = audit_service.generate_html_report(audit_id)
        return HTMLResponse(content=html)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@audit_router.get("/audits")
async def list_audits():
    """
    List all audits
    
    Returns a list of all audit IDs and their basic information
    """
    audits = audit_service.list_audits()
    return JSONResponse({
        "success": True,
        "total_audits": len(audits),
        "audits": audits
    })


@audit_router.get("/health")
async def audit_health_check():
    """Health check for audit service"""
    return {
        "status": "healthy",
        "service": "Architecture Audit API",
        "features": [
            "Architecture pattern detection",
            "API contract analysis",
            "Technology stack audit",
            "HTML report generation",
            "ADR template generation"
        ]
    }
