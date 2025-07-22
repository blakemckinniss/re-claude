"""
Task pattern definitions
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TaskPattern:
    """Pattern for identifying task types"""
    name: str
    keywords: List[str]
    regex_patterns: List[str]
    required_agents: List[str]
    suggested_tools: List[str]
    complexity_modifier: int = 0
    description: str = ""
    
    def matches_keywords(self, text: str) -> int:
        """Count keyword matches in text"""
        text_lower = text.lower()
        return sum(1 for keyword in self.keywords if keyword in text_lower)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "keywords": self.keywords,
            "regex_patterns": self.regex_patterns,
            "required_agents": self.required_agents,
            "suggested_tools": self.suggested_tools,
            "complexity_modifier": self.complexity_modifier,
            "description": self.description
        }


# Predefined task patterns aligned with claude-flow capabilities
TASK_PATTERNS = [
    TaskPattern(
        name="api_development",
        keywords=["api", "endpoint", "rest", "graphql", "service", "backend"],
        regex_patterns=[r"(create|build|develop|implement).*(api|endpoint|service)"],
        required_agents=["coordinator", "architect", "coder", "tester"],
        suggested_tools=["swarm_init", "agent_spawn", "task_orchestrate", "github_repo_analyze"],
        complexity_modifier=1,
        description="API and backend service development"
    ),
    TaskPattern(
        name="frontend_development",
        keywords=["frontend", "ui", "react", "vue", "angular", "component", "interface"],
        regex_patterns=[r"(create|build|design).*(ui|frontend|component|interface)"],
        required_agents=["coordinator", "coder", "designer", "tester"],
        suggested_tools=["swarm_init", "agent_spawn", "workflow_create", "parallel_execute"],
        complexity_modifier=0,
        description="Frontend and UI development"
    ),
    TaskPattern(
        name="database_operations",
        keywords=["database", "db", "sql", "migration", "schema", "query", "optimize"],
        regex_patterns=[r"(create|modify|optimize|migrate).*(database|schema|table)"],
        required_agents=["coordinator", "architect", "specialist", "optimizer"],
        suggested_tools=["memory_persist", "backup_create", "performance_report", "bottleneck_analyze"],
        complexity_modifier=2,
        description="Database design and operations"
    ),
    TaskPattern(
        name="testing_automation",
        keywords=["test", "testing", "qa", "coverage", "unit", "integration", "e2e"],
        regex_patterns=[r"(write|create|implement|add).*(test|testing|coverage)"],
        required_agents=["coordinator", "tester", "reviewer", "monitor"],
        suggested_tools=["workflow_create", "parallel_execute", "benchmark_run", "metrics_collect"],
        complexity_modifier=0,
        description="Testing and quality assurance"
    ),
    TaskPattern(
        name="performance_optimization",
        keywords=["performance", "optimize", "speed", "bottleneck", "efficiency", "scale"],
        regex_patterns=[r"(optimize|improve|enhance).*(performance|speed|efficiency)"],
        required_agents=["coordinator", "optimizer", "analyst", "monitor"],
        suggested_tools=["bottleneck_analyze", "performance_report", "neural_predict", "trend_analysis"],
        complexity_modifier=2,
        description="Performance analysis and optimization"
    ),
    TaskPattern(
        name="security_audit",
        keywords=["security", "audit", "vulnerability", "penetration", "secure", "auth"],
        regex_patterns=[r"(audit|secure|check|scan).*(security|vulnerability|auth)"],
        required_agents=["coordinator", "reviewer", "specialist", "tester"],
        suggested_tools=["security_scan", "github_code_review", "pattern_recognize", "diagnostic_run"],
        complexity_modifier=3,
        description="Security auditing and hardening"
    ),
    TaskPattern(
        name="documentation",
        keywords=["document", "docs", "readme", "guide", "tutorial", "explain"],
        regex_patterns=[r"(write|create|update).*(documentation|docs|readme|guide)"],
        required_agents=["coordinator", "documenter", "reviewer"],
        suggested_tools=["workflow_create", "memory_persist", "github_repo_analyze"],
        complexity_modifier=-1,
        description="Documentation and guides"
    ),
    TaskPattern(
        name="refactoring",
        keywords=["refactor", "restructure", "clean", "improve", "modernize", "migrate"],
        regex_patterns=[r"(refactor|restructure|clean|improve).*(code|architecture|structure)"],
        required_agents=["coordinator", "architect", "coder", "reviewer", "tester"],
        suggested_tools=["github_repo_analyze", "pattern_recognize", "workflow_create", "parallel_execute"],
        complexity_modifier=1,
        description="Code refactoring and modernization"
    ),
    TaskPattern(
        name="deployment",
        keywords=["deploy", "deployment", "ci", "cd", "pipeline", "release", "production"],
        regex_patterns=[r"(deploy|setup|configure).*(pipeline|ci|cd|deployment)"],
        required_agents=["coordinator", "specialist", "monitor", "tester"],
        suggested_tools=["github_workflow_auto", "workflow_create", "scheduler_manage", "health_check"],
        complexity_modifier=2,
        description="Deployment and CI/CD setup"
    ),
    TaskPattern(
        name="data_analysis",
        keywords=["analyze", "data", "analytics", "insights", "report", "visualization"],
        regex_patterns=[r"(analyze|process|visualize).*(data|metrics|insights)"],
        required_agents=["coordinator", "analyst", "researcher", "documenter"],
        suggested_tools=["neural_predict", "pattern_recognize", "trend_analysis", "memory_analytics"],
        complexity_modifier=1,
        description="Data analysis and insights"
    ),
    TaskPattern(
        name="architecture_design",
        keywords=["architecture", "design", "system", "microservice", "distributed", "scale"],
        regex_patterns=[r"(design|architect|plan).*(system|architecture|infrastructure)"],
        required_agents=["coordinator", "architect", "specialist", "reviewer"],
        suggested_tools=["github_repo_analyze", "workflow_create", "pattern_recognize", "memory_persist"],
        complexity_modifier=3,
        description="System architecture and design"
    ),
    TaskPattern(
        name="debugging",
        keywords=["debug", "fix", "bug", "error", "issue", "problem", "troubleshoot"],
        regex_patterns=[r"(debug|fix|solve|troubleshoot).*(bug|error|issue|problem)"],
        required_agents=["coordinator", "coder", "tester", "analyst"],
        suggested_tools=["diagnostic_run", "log_analysis", "pattern_recognize", "github_issue_track"],
        complexity_modifier=1,
        description="Debugging and troubleshooting"
    )
]


def get_pattern_by_name(name: str) -> Optional[TaskPattern]:
    """Get a task pattern by name"""
    for pattern in TASK_PATTERNS:
        if pattern.name == name:
            return pattern
    return None


def get_all_patterns() -> List[TaskPattern]:
    """Get all available task patterns"""
    return TASK_PATTERNS.copy()