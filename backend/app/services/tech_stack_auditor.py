"""
Technology Stack Auditor
Reviews technology choices and generates standardization recommendations
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class TechnologyStack:
    """Technology stack information"""
    databases: List[str] = field(default_factory=list)
    message_queues: List[str] = field(default_factory=list)
    caches: List[str] = field(default_factory=list)
    web_frameworks: List[str] = field(default_factory=list)
    languages: Dict[str, int] = field(default_factory=dict)
    containerization: List[str] = field(default_factory=list)
    ci_cd: List[str] = field(default_factory=list)


class TechStackAuditor:
    """Audits technology stack across services"""
    
    def __init__(self):
        self.tech_patterns = {
            "databases": {
                "PostgreSQL": ["psycopg2", "postgresql", "postgres", "pg"],
                "MySQL": ["mysql", "pymysql", "mysqlclient"],
                "MongoDB": ["mongodb", "pymongo", "mongoose"],
                "Redis": ["redis", "ioredis"],
                "SQLite": ["sqlite3", "sqlite"],
                "Cassandra": ["cassandra", "pycassa"],
                "Elasticsearch": ["elasticsearch", "elastic"],
                "DynamoDB": ["dynamodb", "boto3"]
            },
            "message_queues": {
                "RabbitMQ": ["rabbitmq", "pika", "amqp"],
                "Kafka": ["kafka", "kafka-python", "kafkajs"],
                "Redis Pub/Sub": ["redis"],
                "AWS SQS": ["sqs", "boto3"],
                "Google Pub/Sub": ["pubsub"],
                "NATS": ["nats"]
            },
            "caches": {
                "Redis": ["redis", "ioredis"],
                "Memcached": ["memcached", "pymemcache"],
                "Varnish": ["varnish"],
                "CDN": ["cloudflare", "cloudfront", "fastly"]
            },
            "web_frameworks": {
                "FastAPI": ["fastapi"],
                "Flask": ["flask"],
                "Django": ["django"],
                "Express": ["express"],
                "NestJS": ["@nestjs/core"],
                "Spring Boot": ["spring-boot"],
                "Gin": ["gin-gonic"],
                "Echo": ["echo"]
            }
        }
    
    def analyze_directory(self, directory_path: str) -> Dict:
        """Analyze technology stack in a directory"""
        path = Path(directory_path)
        
        if not path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        stack = self._detect_technologies(path)
        
        return {
            "directory": str(path),
            "technology_stack": {
                "databases": stack.databases,
                "message_queues": stack.message_queues,
                "caches": stack.caches,
                "web_frameworks": stack.web_frameworks,
                "languages": stack.languages,
                "containerization": stack.containerization,
                "ci_cd": stack.ci_cd
            },
            "configuration_files": self._find_config_files(path),
            "recommendations": self._generate_recommendations(stack)
        }
    
    def _detect_technologies(self, path: Path) -> TechnologyStack:
        """Detect technologies used in the project"""
        stack = TechnologyStack()
        
        # Analyze Python dependencies
        requirements_file = path / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    content = f.read().lower()
                    self._scan_dependencies(content, stack)
                    stack.languages["Python"] = stack.languages.get("Python", 0) + 1
            except:
                pass
        
        # Analyze JavaScript/Node.js dependencies
        package_json = path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    deps_str = ' '.join(dependencies.keys()).lower()
                    self._scan_dependencies(deps_str, stack)
                    stack.languages["JavaScript/TypeScript"] = stack.languages.get("JavaScript/TypeScript", 0) + 1
            except:
                pass
        
        # Analyze Go modules
        go_mod = path / "go.mod"
        if go_mod.exists():
            try:
                with open(go_mod, 'r') as f:
                    content = f.read().lower()
                    self._scan_dependencies(content, stack)
                    stack.languages["Go"] = stack.languages.get("Go", 0) + 1
            except:
                pass
        
        # Check for containerization
        if (path / "Dockerfile").exists():
            stack.containerization.append("Docker")
        if (path / "docker-compose.yml").exists() or (path / "docker-compose.yaml").exists():
            stack.containerization.append("Docker Compose")
        if (path / "kubernetes").exists() or (path / "k8s").exists():
            stack.containerization.append("Kubernetes")
        
        # Check for CI/CD
        if (path / ".github" / "workflows").exists():
            stack.ci_cd.append("GitHub Actions")
        if (path / ".gitlab-ci.yml").exists():
            stack.ci_cd.append("GitLab CI")
        if (path / "Jenkinsfile").exists():
            stack.ci_cd.append("Jenkins")
        if (path / ".circleci").exists():
            stack.ci_cd.append("CircleCI")
        
        return stack
    
    def _scan_dependencies(self, content: str, stack: TechnologyStack):
        """Scan dependency content for technology patterns"""
        for category, techs in self.tech_patterns.items():
            for tech_name, patterns in techs.items():
                for pattern in patterns:
                    if pattern in content:
                        target_list = getattr(stack, category)
                        if tech_name not in target_list:
                            target_list.append(tech_name)
                        break
    
    def _find_config_files(self, path: Path) -> List[str]:
        """Find configuration files"""
        config_files = []
        
        config_patterns = [
            '*.yaml', '*.yml', '*.json', '*.toml', '*.ini', 
            '.env*', 'config.*', 'settings.*'
        ]
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', '.venv']]
            
            for file in files:
                for pattern in config_patterns:
                    if self._match_pattern(file, pattern):
                        file_path = Path(root) / file
                        config_files.append(str(file_path.relative_to(path)))
                        break
        
        return config_files[:20]  # Limit to 20 examples
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Match filename against pattern"""
        if '*' in pattern:
            pattern_regex = pattern.replace('.', r'\.').replace('*', '.*')
            return re.match(f'^{pattern_regex}$', filename) is not None
        return filename == pattern
    
    def _generate_recommendations(self, stack: TechnologyStack) -> List[str]:
        """Generate standardization recommendations"""
        recommendations = []
        
        # Database recommendations
        if len(stack.databases) > 2:
            recommendations.append(
                f"Multiple database types detected ({', '.join(stack.databases)}). "
                "Consider standardizing on 1-2 database solutions for easier maintenance."
            )
        
        # Message queue recommendations
        if len(stack.message_queues) > 1:
            recommendations.append(
                f"Multiple message queue solutions detected ({', '.join(stack.message_queues)}). "
                "Consider standardizing on a single message queue for consistency."
            )
        
        # Cache recommendations
        if not stack.caches:
            recommendations.append(
                "No caching solution detected. Consider implementing Redis or Memcached for performance."
            )
        
        # Containerization recommendations
        if not stack.containerization:
            recommendations.append(
                "No containerization detected. Consider using Docker for consistent deployments."
            )
        elif "Docker" in stack.containerization and "Kubernetes" not in stack.containerization:
            recommendations.append(
                "Docker detected but no orchestration. Consider Kubernetes for production deployments."
            )
        
        # CI/CD recommendations
        if not stack.ci_cd:
            recommendations.append(
                "No CI/CD pipeline detected. Consider implementing automated testing and deployment."
            )
        
        return recommendations
    
    def compare_stacks(self, stacks: List[Dict]) -> Dict:
        """Compare technology stacks across multiple services"""
        all_databases = set()
        all_queues = set()
        all_caches = set()
        all_frameworks = set()
        all_languages = set()
        
        for stack_data in stacks:
            stack = stack_data.get('technology_stack', {})
            all_databases.update(stack.get('databases', []))
            all_queues.update(stack.get('message_queues', []))
            all_caches.update(stack.get('caches', []))
            all_frameworks.update(stack.get('web_frameworks', []))
            all_languages.update(stack.get('languages', {}).keys())
        
        return {
            "databases": {
                "count": len(all_databases),
                "list": sorted(all_databases),
                "standardization_score": 1.0 / max(len(all_databases), 1)
            },
            "message_queues": {
                "count": len(all_queues),
                "list": sorted(all_queues),
                "standardization_score": 1.0 / max(len(all_queues), 1)
            },
            "caches": {
                "count": len(all_caches),
                "list": sorted(all_caches),
                "standardization_score": 1.0 / max(len(all_caches), 1)
            },
            "web_frameworks": {
                "count": len(all_frameworks),
                "list": sorted(all_frameworks),
                "diversity": len(all_frameworks)
            },
            "languages": {
                "count": len(all_languages),
                "list": sorted(all_languages)
            },
            "overall_standardization": self._calculate_overall_score(
                len(all_databases), len(all_queues), len(all_caches)
            )
        }
    
    def _calculate_overall_score(self, db_count: int, queue_count: int, cache_count: int) -> float:
        """Calculate overall standardization score"""
        # Lower counts mean better standardization
        ideal_counts = [1, 1, 1]  # Ideal is 1 of each
        actual_counts = [db_count or 1, queue_count or 1, cache_count or 1]
        
        scores = [ideal / actual for ideal, actual in zip(ideal_counts, actual_counts)]
        return round(sum(scores) / len(scores), 2)


# Singleton instance
tech_stack_auditor = TechStackAuditor()
