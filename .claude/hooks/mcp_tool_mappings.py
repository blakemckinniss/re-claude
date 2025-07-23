"""
MCP Tool Mappings - Defines required tools for specific task patterns

This mapping enforces the use of claude-flow's 87 MCP tools based on task context.
"""

# Task pattern to required MCP tools mapping
TASK_PATTERN_TOOLS = {
    "api_development": {
        "required": [
            "workflow_create",  # API workflow design
            "github_repo_analyze",  # Analyze existing API structure
            "pattern_recognize",  # Identify API patterns
            "memory_usage"  # Store API design decisions
        ],
        "recommended": [
            "parallel_execute",  # Execute API tests in parallel
            "performance_report",  # API performance metrics
            "bottleneck_analyze",  # Find API bottlenecks
            "health_check"  # API health monitoring
        ]
    },
    "frontend_development": {
        "required": [
            "workflow_create",  # UI component workflow
            "cognitive_analyze",  # UX pattern analysis
            "pattern_recognize",  # UI pattern detection
            "memory_usage"  # Store design decisions
        ],
        "recommended": [
            "github_code_review",  # Review component code
            "trend_analysis",  # UI/UX trends
            "features_detect"  # Feature compatibility
        ]
    },
    "backend_development": {
        "required": [
            "workflow_create",  # Backend service workflow
            "github_repo_analyze",  # Analyze service structure
            "bottleneck_analyze",  # Performance analysis
            "memory_usage"  # Store architectural decisions
        ],
        "recommended": [
            "performance_report",  # Service metrics
            "health_check",  # Service health
            "diagnostic_run",  # Troubleshooting
            "log_analysis"  # Log examination
        ]
    },
    "database_operations": {
        "required": [
            "backup_create",  # Database backup first!
            "workflow_create",  # Migration workflow
            "pattern_recognize",  # Schema patterns
            "memory_usage"  # Track schema changes
        ],
        "recommended": [
            "performance_report",  # Query performance
            "bottleneck_analyze",  # Slow queries
            "trend_analysis"  # Usage patterns
        ]
    },
    "testing_automation": {
        "required": [
            "benchmark_run",  # Performance benchmarks
            "parallel_execute",  # Parallel test execution
            "diagnostic_run",  # Test diagnostics
            "health_check"  # System health
        ],
        "recommended": [
            "workflow_create",  # Test workflows
            "metrics_collect",  # Test metrics
            "trend_analysis",  # Test trends
            "github_workflow_auto"  # CI/CD integration
        ]
    },
    "performance_optimization": {
        "required": [
            "bottleneck_analyze",  # Find bottlenecks
            "performance_report",  # Current metrics
            "benchmark_run",  # Performance baseline
            "neural_predict"  # Predict optimizations
        ],
        "recommended": [
            "wasm_optimize",  # WASM optimization
            "neural_compress",  # Model compression
            "memory_compress",  # Memory optimization
            "trend_analysis"  # Performance trends
        ]
    },
    "security_audit": {
        "required": [
            "security_scan",  # Security vulnerabilities
            "github_code_review",  # Code security review
            "log_analysis",  # Security log analysis
            "config_manage"  # Configuration audit
        ],
        "recommended": [
            "pattern_recognize",  # Attack patterns
            "cognitive_analyze",  # Threat analysis
            "backup_create",  # Pre-audit backup
            "memory_usage"  # Track findings
        ]
    },
    "documentation": {
        "required": [
            "github_repo_analyze",  # Analyze codebase
            "pattern_recognize",  # Code patterns
            "workflow_create",  # Doc generation workflow
            "memory_usage"  # Store doc context
        ],
        "recommended": [
            "cognitive_analyze",  # Content analysis
            "trend_analysis"  # Documentation trends
        ]
    },
    "debugging": {
        "required": [
            "diagnostic_run",  # Run diagnostics
            "log_analysis",  # Analyze logs
            "memory_search",  # Search debug history
            "pattern_recognize"  # Error patterns
        ],
        "recommended": [
            "cognitive_analyze",  # Root cause analysis
            "neural_predict",  # Predict issues
            "health_check",  # System health
            "bottleneck_analyze"  # Performance issues
        ]
    },
    "deployment": {
        "required": [
            "workflow_create",  # Deployment workflow
            "parallel_execute",  # Parallel deployments
            "health_check",  # Post-deploy health
            "backup_create"  # Pre-deploy backup
        ],
        "recommended": [
            "github_workflow_auto",  # CI/CD automation
            "scheduler_manage",  # Deployment scheduling
            "trigger_setup",  # Deploy triggers
            "metrics_collect"  # Deploy metrics
        ]
    },
    "refactoring": {
        "required": [
            "github_repo_analyze",  # Analyze code structure
            "pattern_recognize",  # Code patterns
            "cognitive_analyze",  # Refactor analysis
            "backup_create"  # Pre-refactor backup
        ],
        "recommended": [
            "github_code_review",  # Review changes
            "workflow_create",  # Refactor workflow
            "memory_usage",  # Track decisions
            "trend_analysis"  # Code trends
        ]
    },
    "architecture_design": {
        "required": [
            "github_repo_analyze",  # Current architecture
            "pattern_recognize",  # Architectural patterns
            "cognitive_analyze",  # Design analysis
            "workflow_create"  # Implementation workflow
        ],
        "recommended": [
            "daa_agent_create",  # Dynamic agents
            "ensemble_create",  # Model ensembles
            "neural_train",  # Train patterns
            "memory_usage"  # Store decisions
        ]
    }
}

# Complexity-based required tools
COMPLEXITY_REQUIRED_TOOLS = {
    1: [],  # Trivial - no MCP tools required
    2: ["memory_usage"],  # Simple - just memory
    3: ["memory_usage", "swarm_init"],  # Basic coordination
    4: ["memory_usage", "swarm_init", "agent_spawn", "task_orchestrate"],
    5: ["memory_usage", "swarm_init", "agent_spawn", "task_orchestrate", "workflow_create"],
    6: ["memory_usage", "swarm_init", "agent_spawn", "task_orchestrate", "workflow_create", "coordination_sync"],
    7: ["memory_usage", "swarm_init", "agent_spawn", "task_orchestrate", "workflow_create", "coordination_sync", "cognitive_analyze"],
    8: ["memory_usage", "swarm_init", "agent_spawn", "task_orchestrate", "workflow_create", "coordination_sync", "cognitive_analyze", "neural_predict"],
    9: ["memory_usage", "swarm_init", "agent_spawn", "task_orchestrate", "workflow_create", "coordination_sync", "cognitive_analyze", "neural_predict", "hive_mind_spawn"],
    10: ["memory_usage", "swarm_init", "agent_spawn", "task_orchestrate", "workflow_create", "coordination_sync", "cognitive_analyze", "neural_predict", "hive_mind_spawn", "daa_agent_create"]
}

# Agent role to required tools
AGENT_REQUIRED_TOOLS = {
    "coordinator": ["task_orchestrate", "coordination_sync"],
    "researcher": ["memory_search", "pattern_recognize"],
    "coder": ["github_code_review"],
    "tester": ["benchmark_run", "diagnostic_run"],
    "optimizer": ["bottleneck_analyze", "performance_report"],
    "analyst": ["cognitive_analyze", "trend_analysis"],
    "architect": ["pattern_recognize", "github_repo_analyze"],
    "reviewer": ["security_scan", "github_code_review"],
    "monitor": ["health_check", "metrics_collect"],
    "documenter": ["github_repo_analyze"],
    "designer": ["pattern_recognize", "cognitive_analyze"],
    "specialist": ["daa_capability_match", "features_detect"]
}

def get_required_tools(patterns: list, complexity: int, agent_roles: list) -> list:
    """Get all required MCP tools based on task context"""
    required = set()
    
    # Add pattern-based requirements
    for pattern in patterns:
        pattern_name = pattern.name if hasattr(pattern, 'name') else pattern
        if pattern_name in TASK_PATTERN_TOOLS:
            required.update(TASK_PATTERN_TOOLS[pattern_name]["required"])
    
    # Add complexity-based requirements
    if complexity in COMPLEXITY_REQUIRED_TOOLS:
        required.update(COMPLEXITY_REQUIRED_TOOLS[complexity])
    
    # Add agent-based requirements
    for role in agent_roles:
        if role in AGENT_REQUIRED_TOOLS:
            required.update(AGENT_REQUIRED_TOOLS[role])
    
    return sorted(list(required))