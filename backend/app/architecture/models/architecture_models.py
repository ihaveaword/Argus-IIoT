"""
Data models for architecture analysis results
"""
from typing import List, Dict, Optional, Set
from pydantic import BaseModel, Field
from enum import Enum


class ArchitecturePattern(str, Enum):
    """Supported architecture patterns"""
    MVC = "MVC"
    HEXAGONAL = "Hexagonal"
    CLEAN_ARCHITECTURE = "Clean Architecture"
    DDD = "Domain-Driven Design"
    LAYERED = "Layered Architecture"
    MICROKERNEL = "Microkernel"
    EVENT_DRIVEN = "Event-Driven"
    UNKNOWN = "Unknown"


class APIType(str, Enum):
    """API protocol types"""
    REST = "REST"
    GRPC = "gRPC"
    GRAPHQL = "GraphQL"
    WEBSOCKET = "WebSocket"
    UNKNOWN = "Unknown"


class TechStackCategory(str, Enum):
    """Technology stack categories"""
    DATABASE = "Database"
    MESSAGE_QUEUE = "Message Queue"
    CACHE = "Cache"
    WEB_FRAMEWORK = "Web Framework"
    LANGUAGE = "Programming Language"
    OTHER = "Other"


class ServiceDependency(BaseModel):
    """Service dependency information"""
    source_service: str
    target_service: str
    dependency_type: str = Field(description="sync, async, or event")
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class APIEndpoint(BaseModel):
    """API endpoint definition"""
    method: str
    path: str
    api_type: APIType
    request_schema: Optional[Dict] = None
    response_schema: Optional[Dict] = None
    service_name: str
    file_location: Optional[str] = None


class BreakingChange(BaseModel):
    """API breaking change detection"""
    endpoint: str
    change_type: str
    description: str
    affected_services: List[str]
    severity: str = Field(description="high, medium, low")


class TechStackItem(BaseModel):
    """Technology stack item"""
    name: str
    version: Optional[str] = None
    category: TechStackCategory
    service_name: str


class CircularDependency(BaseModel):
    """Circular dependency in service calls"""
    services: List[str]
    description: str


class PerformanceBottleneck(BaseModel):
    """Performance bottleneck detection"""
    service_name: str
    bottleneck_type: str
    description: str
    severity: str = Field(description="high, medium, low")


class RepositoryAnalysis(BaseModel):
    """Analysis result for a single repository"""
    repo_name: str
    repo_url: str
    architecture_patterns: List[ArchitecturePattern]
    pattern_confidence: Dict[str, float] = Field(default_factory=dict)
    api_endpoints: List[APIEndpoint] = Field(default_factory=list)
    tech_stack: List[TechStackItem] = Field(default_factory=list)
    services: List[str] = Field(default_factory=list)
    file_structure: Dict[str, List[str]] = Field(default_factory=dict)


class SystemTopology(BaseModel):
    """System-wide service topology"""
    services: List[str]
    dependencies: List[ServiceDependency]
    circular_dependencies: List[CircularDependency] = Field(default_factory=list)
    bottlenecks: List[PerformanceBottleneck] = Field(default_factory=list)


class APICompatibilityReport(BaseModel):
    """API compatibility analysis report"""
    total_endpoints: int
    breaking_changes: List[BreakingChange] = Field(default_factory=list)
    api_standards_violations: List[str] = Field(default_factory=list)


class TechStackReport(BaseModel):
    """Technology stack standardization report"""
    tech_items: List[TechStackItem]
    standardization_recommendations: List[str] = Field(default_factory=list)
    version_conflicts: List[str] = Field(default_factory=list)


class ArchitectureAuditReport(BaseModel):
    """Complete architecture audit report"""
    repositories: List[RepositoryAnalysis]
    topology: SystemTopology
    api_report: APICompatibilityReport
    tech_stack_report: TechStackReport
    timestamp: str
    total_services: int = 0
    total_repositories: int = 0
