"""
Technology Stack Analyzer
Analyzes technology choices and generates standardization recommendations
"""
import os
import re
import json
from typing import List, Dict, Set
from collections import defaultdict

from app.architecture.models.architecture_models import (
    TechStackItem, TechStackCategory, TechStackReport
)


class TechStackAnalyzer:
    """Analyzes technology stack across repositories"""
    
    def __init__(self):
        # Technology detection patterns
        self.tech_patterns = {
            TechStackCategory.DATABASE: {
                'PostgreSQL': [r'postgresql', r'psycopg2', r'pg'],
                'MySQL': [r'mysql', r'pymysql'],
                'MongoDB': [r'mongodb', r'mongoose', r'pymongo'],
                'Redis': [r'redis', r'ioredis'],
                'Elasticsearch': [r'elasticsearch', r'elastic'],
                'Cassandra': [r'cassandra'],
                'SQLite': [r'sqlite'],
            },
            TechStackCategory.MESSAGE_QUEUE: {
                'RabbitMQ': [r'rabbitmq', r'amqp', r'pika'],
                'Kafka': [r'kafka', r'confluent'],
                'Redis': [r'redis.*queue', r'bull', r'bee-queue'],
                'AWS SQS': [r'aws.*sqs', r'boto3.*sqs'],
                'NATS': [r'nats'],
                'ZeroMQ': [r'zeromq', r'zmq'],
            },
            TechStackCategory.CACHE: {
                'Redis': [r'redis'],
                'Memcached': [r'memcached'],
                'Varnish': [r'varnish'],
                'Ehcache': [r'ehcache'],
            },
            TechStackCategory.WEB_FRAMEWORK: {
                'FastAPI': [r'fastapi'],
                'Flask': [r'flask'],
                'Django': [r'django'],
                'Express': [r'express'],
                'Spring Boot': [r'spring.*boot', r'@SpringBootApplication'],
                'ASP.NET': [r'asp\.net', r'Microsoft\.AspNetCore'],
                'Gin': [r'github\.com/gin-gonic/gin'],
                'Vue': [r'vue', r'@vue/'],
                'React': [r'react', r'react-dom'],
                'Angular': [r'@angular/'],
            },
            TechStackCategory.LANGUAGE: {
                'Python': [r'python', r'\.py$'],
                'JavaScript': [r'javascript', r'\.js$'],
                'TypeScript': [r'typescript', r'\.ts$'],
                'Java': [r'java', r'\.java$'],
                'Go': [r'golang', r'\.go$'],
                'C#': [r'\.cs$', r'csharp'],
                'Ruby': [r'ruby', r'\.rb$'],
                'PHP': [r'php', r'\.php$'],
            },
        }
    
    def analyze_package_file(self, file_path: str, service_name: str) -> List[TechStackItem]:
        """Analyze package management files"""
        tech_items = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if file_path.endswith('requirements.txt'):
                    # Python requirements
                    tech_items.extend(self._parse_requirements_txt(content, service_name))
                elif file_path.endswith('package.json'):
                    # Node.js package.json
                    tech_items.extend(self._parse_package_json(content, service_name))
                elif file_path.endswith('pom.xml'):
                    # Maven pom.xml
                    tech_items.extend(self._parse_pom_xml(content, service_name))
                elif file_path.endswith('go.mod'):
                    # Go modules
                    tech_items.extend(self._parse_go_mod(content, service_name))
                elif file_path.endswith('.csproj'):
                    # .NET project
                    tech_items.extend(self._parse_csproj(content, service_name))
        except Exception:
            pass
        
        return tech_items
    
    def _parse_requirements_txt(self, content: str, service_name: str) -> List[TechStackItem]:
        """Parse Python requirements.txt"""
        tech_items = []
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse package==version or package>=version
            match = re.match(r'([a-zA-Z0-9_-]+)([=<>!]+)([0-9.]+)', line)
            if match:
                package_name = match.group(1)
                version = match.group(3)
                category = self._categorize_tech(package_name)
                
                tech_items.append(TechStackItem(
                    name=package_name,
                    version=version,
                    category=category,
                    service_name=service_name
                ))
        
        return tech_items
    
    def _parse_package_json(self, content: str, service_name: str) -> List[TechStackItem]:
        """Parse Node.js package.json"""
        tech_items = []
        
        try:
            data = json.loads(content)
            dependencies = data.get('dependencies', {})
            dev_dependencies = data.get('devDependencies', {})
            
            all_deps = {**dependencies, **dev_dependencies}
            
            for package_name, version in all_deps.items():
                # Clean version string
                version = version.lstrip('^~>=<')
                category = self._categorize_tech(package_name)
                
                tech_items.append(TechStackItem(
                    name=package_name,
                    version=version,
                    category=category,
                    service_name=service_name
                ))
        except json.JSONDecodeError:
            pass
        
        return tech_items
    
    def _parse_pom_xml(self, content: str, service_name: str) -> List[TechStackItem]:
        """Parse Maven pom.xml"""
        tech_items = []
        
        # Extract dependencies
        dep_pattern = r'<dependency>\s*<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>\s*<version>([^<]+)</version>'
        matches = re.finditer(dep_pattern, content, re.DOTALL)
        
        for match in matches:
            group_id = match.group(1).strip()
            artifact_id = match.group(2).strip()
            version = match.group(3).strip()
            
            package_name = f"{group_id}:{artifact_id}"
            category = self._categorize_tech(artifact_id)
            
            tech_items.append(TechStackItem(
                name=package_name,
                version=version,
                category=category,
                service_name=service_name
            ))
        
        return tech_items
    
    def _parse_go_mod(self, content: str, service_name: str) -> List[TechStackItem]:
        """Parse Go go.mod"""
        tech_items = []
        
        # Extract require statements
        require_pattern = r'require\s+([^\s]+)\s+v([0-9.]+)'
        matches = re.finditer(require_pattern, content)
        
        for match in matches:
            package_name = match.group(1)
            version = match.group(2)
            category = self._categorize_tech(package_name)
            
            tech_items.append(TechStackItem(
                name=package_name,
                version=version,
                category=category,
                service_name=service_name
            ))
        
        return tech_items
    
    def _parse_csproj(self, content: str, service_name: str) -> List[TechStackItem]:
        """Parse .NET .csproj"""
        tech_items = []
        
        # Extract PackageReference
        package_pattern = r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"'
        matches = re.finditer(package_pattern, content)
        
        for match in matches:
            package_name = match.group(1)
            version = match.group(2)
            category = self._categorize_tech(package_name)
            
            tech_items.append(TechStackItem(
                name=package_name,
                version=version,
                category=category,
                service_name=service_name
            ))
        
        return tech_items
    
    def _categorize_tech(self, package_name: str) -> TechStackCategory:
        """Categorize technology based on package name"""
        package_lower = package_name.lower()
        
        for category, tech_dict in self.tech_patterns.items():
            for tech_name, patterns in tech_dict.items():
                for pattern in patterns:
                    if re.search(pattern, package_lower, re.IGNORECASE):
                        return category
        
        return TechStackCategory.OTHER
    
    def analyze_repository(self, repo_path: str, service_name: str) -> List[TechStackItem]:
        """Analyze repository for technology stack"""
        tech_items = []
        
        if not os.path.exists(repo_path):
            return tech_items
        
        # Look for package management files
        package_files = [
            'requirements.txt', 'package.json', 'pom.xml', 
            'go.mod', 'Gemfile', 'composer.json'
        ]
        
        for root, dirs, files in os.walk(repo_path):
            # Skip non-relevant directories
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '__pycache__', '.git']]
            
            for file_name in files:
                if file_name in package_files or file_name.endswith('.csproj'):
                    file_path = os.path.join(root, file_name)
                    items = self.analyze_package_file(file_path, service_name)
                    tech_items.extend(items)
        
        return tech_items
    
    def generate_standardization_report(self, all_tech_items: List[TechStackItem]) -> TechStackReport:
        """Generate technology standardization recommendations"""
        recommendations = []
        version_conflicts = []
        
        # Group by technology name
        tech_by_name = defaultdict(list)
        for item in all_tech_items:
            tech_by_name[item.name].append(item)
        
        # Detect version conflicts
        for tech_name, items in tech_by_name.items():
            versions = set(item.version for item in items if item.version)
            if len(versions) > 1:
                services = [item.service_name for item in items]
                version_conflicts.append(
                    f"{tech_name} has version conflicts: {', '.join(versions)} across services: {', '.join(set(services))}"
                )
        
        # Count technology usage by category
        category_counts = defaultdict(lambda: defaultdict(int))
        for item in all_tech_items:
            category_counts[item.category][item.name] += 1
        
        # Generate recommendations for standardization
        for category, tech_counts in category_counts.items():
            if len(tech_counts) > 3:  # Multiple technologies in same category
                most_common = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)
                recommendations.append(
                    f"{category.value}: Consider standardizing on {most_common[0][0]} "
                    f"(used by {most_common[0][1]} services). "
                    f"Currently using {len(tech_counts)} different technologies."
                )
        
        return TechStackReport(
            tech_items=all_tech_items,
            standardization_recommendations=recommendations,
            version_conflicts=version_conflicts
        )
