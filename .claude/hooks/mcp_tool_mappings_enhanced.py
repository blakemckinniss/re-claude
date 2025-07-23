"""
Enhanced MCP Tool Mappings - Prioritizes context7 and exa for maximum information gathering
"""

from typing import List, Dict, Any

# Original mappings (preserved)
from mcp_tool_mappings import TASK_PATTERN_TOOLS as ORIGINAL_PATTERN_TOOLS
from mcp_tool_mappings import COMPLEXITY_REQUIRED_TOOLS as ORIGINAL_COMPLEXITY_TOOLS
from mcp_tool_mappings import AGENT_REQUIRED_TOOLS as ORIGINAL_AGENT_TOOLS


# Enhanced pattern mappings that prioritize context7 and exa
ENHANCED_PATTERN_TOOLS = {
    # Any development task should use context7 for docs
    "api_development": {
        "required": [
            "mcp__context7__resolve-library-id",  # Find library docs
            "mcp__context7__get-library-docs",    # Get API documentation
            "mcp__exa__web_search_exa",          # Search for best practices
            "workflow_create",
            "memory_usage"
        ],
        "recommended": ORIGINAL_PATTERN_TOOLS.get("api_development", {}).get("recommended", [])
    },
    "frontend_development": {
        "required": [
            "mcp__context7__resolve-library-id",  # Find React/Vue/Angular docs
            "mcp__context7__get-library-docs",    # Get framework docs
            "mcp__exa__web_search_exa",          # Search UI patterns
            "workflow_create",
            "cognitive_analyze",
            "memory_usage"
        ],
        "recommended": ORIGINAL_PATTERN_TOOLS.get("frontend_development", {}).get("recommended", [])
    },
    "backend_development": {
        "required": [
            "mcp__context7__resolve-library-id",  # Find server framework docs
            "mcp__context7__get-library-docs",    # Get backend docs
            "mcp__exa__web_search_exa",          # Search architecture patterns
            "workflow_create",
            "bottleneck_analyze",
            "memory_usage"
        ],
        "recommended": ORIGINAL_PATTERN_TOOLS.get("backend_development", {}).get("recommended", [])
    },
    "debugging": {
        "required": [
            "mcp__exa__web_search_exa",          # Search for similar issues
            "mcp__context7__resolve-library-id",  # Find library docs for errors
            "mcp__context7__get-library-docs",    # Get relevant docs
            "diagnostic_run",
            "log_analysis",
            "memory_search"
        ],
        "recommended": ORIGINAL_PATTERN_TOOLS.get("debugging", {}).get("recommended", [])
    },
    "code_analysis": {
        "required": [
            "mcp__exa__web_search_exa",  # Best practices
            "cognitive_analyze",
            "pattern_recognize",
            "memory_usage"
        ],
        "recommended": ["quality_assess", "bottleneck_analyze"]
    },
    "documentation_generation": {
        "required": [
            "mcp__context7__resolve-library-id",  # Library references
            "mcp__exa__web_search_exa",  # Documentation examples
            "workflow_create",
            "memory_usage"
        ],
        "recommended": ["github_repo_analyze"]
    },
    "code_review": {
        "required": [
            "mcp__exa__web_search_exa",  # Best practices
            "github_code_review",
            "quality_assess",
            "memory_usage"
        ],
        "recommended": ["security_scan", "performance_report"]
    },
    # Add context7 and exa to all other patterns
    **{
        pattern: {
            "required": [
                "mcp__exa__web_search_exa",  # Always search for current info
                *tools.get("required", [])
            ],
            "recommended": [
                "mcp__context7__resolve-library-id",
                "mcp__context7__get-library-docs",
                *tools.get("recommended", [])
            ]
        }
        for pattern, tools in ORIGINAL_PATTERN_TOOLS.items()
        if pattern not in ["api_development", "frontend_development", "backend_development", "debugging"]
    }
}

# Enhanced complexity-based tools - add context7 and exa at all levels
ENHANCED_COMPLEXITY_TOOLS = {
    1: ["mcp__exa__web_search_exa"],  # Even simple tasks benefit from search
    2: ["memory_usage", "mcp__exa__web_search_exa"],
    3: ["memory_usage", "swarm_init", "mcp__exa__web_search_exa"],
    4: ["memory_usage", "swarm_init", "agent_spawn", "task_orchestrate", 
        "mcp__context7__resolve-library-id", "mcp__exa__web_search_exa"],
    5: ["memory_usage", "swarm_init", "agent_spawn", "task_orchestrate", "workflow_create",
        "mcp__context7__get-library-docs", "mcp__exa__web_search_exa"],
    # For higher complexity, always include both context7 and exa
    **{
        level: [
            "mcp__context7__resolve-library-id",
            "mcp__context7__get-library-docs", 
            "mcp__exa__web_search_exa",
            *tools
        ]
        for level, tools in ORIGINAL_COMPLEXITY_TOOLS.items()
        if level > 5
    }
}

# Enhanced agent-based tools
ENHANCED_AGENT_TOOLS = {
    "coordinator": ["task_orchestrate", "coordination_sync", "mcp__exa__web_search_exa"],
    "researcher": ["memory_search", "pattern_recognize", "mcp__exa__web_search_exa", 
                   "mcp__context7__resolve-library-id", "mcp__context7__get-library-docs"],
    "coder": ["github_code_review", "mcp__context7__get-library-docs", "mcp__exa__web_search_exa"],
    "analyst": ["cognitive_analyze", "trend_analysis", "mcp__exa__web_search_exa"],
    "documenter": ["github_repo_analyze", "mcp__context7__resolve-library-id", 
                   "mcp__context7__get-library-docs", "mcp__exa__web_search_exa"],
    # Add exa to all other agents
    **{
        agent: [*tools, "mcp__exa__web_search_exa"]
        for agent, tools in ORIGINAL_AGENT_TOOLS.items()
        if agent not in ["coordinator", "researcher", "coder", "analyst", "documenter"]
    }
}

def get_enhanced_required_tools(patterns: list, complexity: int, agent_roles: list) -> list:
    """Enhanced version that always includes context7 and exa tools"""
    required = set()
    
    # Always start with exa for any task
    required.add("mcp__exa__web_search_exa")
    
    # Add pattern-based requirements
    for pattern in patterns:
        pattern_name = pattern.name if hasattr(pattern, 'name') else pattern
        if pattern_name in ENHANCED_PATTERN_TOOLS:
            required.update(ENHANCED_PATTERN_TOOLS[pattern_name]["required"])
    
    # Add complexity-based requirements
    if complexity in ENHANCED_COMPLEXITY_TOOLS:
        required.update(ENHANCED_COMPLEXITY_TOOLS[complexity])
    
    # Add agent-based requirements
    for role in agent_roles:
        if role in ENHANCED_AGENT_TOOLS:
            required.update(ENHANCED_AGENT_TOOLS[role])
    
    # If any code-related patterns, always add context7
    code_patterns = ["api_development", "frontend_development", "backend_development",
                     "debugging", "refactoring", "testing_automation"]
    if any(p.name if hasattr(p, 'name') else p in code_patterns for p in patterns):
        required.add("mcp__context7__resolve-library-id")
        required.add("mcp__context7__get-library-docs")
    
    return list(required)
    
# Keywords that trigger context7, exa
CONTEXT7_TRIGGERS = [
    "library", "framework", "package", "module", "api", "sdk", "documentation",
    "how to", "how do", "example", "tutorial", "guide", "reference", "docs",
    "usage", "syntax", "method", "function", "class", "interface", "hook",
    "component", "react", "vue", "angular", "express", "django", "flask"
]

EXA_TRIGGERS = [
    "search", "find", "latest", "current", "best practice", "solution",
    "alternative", "compare", "vs", "versus", "recommend", "suggestion",
    "how", "what", "why", "when", "should", "could", "would", "error",
    "bug", "issue", "problem", "fix", "solve", "debug", "help"
]

def should_use_context7(prompt: str) -> bool:
    """Check if prompt should trigger context7 usage"""
    prompt_lower = prompt.lower()
    # Check each keyword
    for trigger in CONTEXT7_TRIGGERS:
        if trigger.lower() in prompt_lower:
            return True
    return False

def should_use_exa(prompt: str) -> bool:
    """Check if prompt should trigger exa usage"""
    prompt_lower = prompt.lower()
    # Check each keyword
    for trigger in EXA_TRIGGERS:
        if trigger.lower() in prompt_lower:
            return True
    return False

# Export enhanced versions as the main functions
get_required_tools = get_enhanced_required_tools
TASK_PATTERN_TOOLS = ENHANCED_PATTERN_TOOLS
COMPLEXITY_REQUIRED_TOOLS = ENHANCED_COMPLEXITY_TOOLS
AGENT_REQUIRED_TOOLS = ENHANCED_AGENT_TOOLS