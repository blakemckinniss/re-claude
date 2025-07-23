"""
Advanced task analysis with claude-flow patterns
"""

import re
import sys
import os
from typing import List, Tuple, Dict, Any, Optional
from ..models.patterns import TaskPattern, TASK_PATTERNS
from ..models.analysis import TaskComplexity

# Import MCP tool mappings
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from mcp_tool_mappings import get_required_tools, TASK_PATTERN_TOOLS
except ImportError:
    # Fallback if mappings not available
    get_required_tools = None
    TASK_PATTERN_TOOLS = {}


class TaskAnalyzer:
    """Enhanced task analyzer with claude-flow patterns"""
    
    def __init__(self, patterns: Optional[List[TaskPattern]] = None):
        self.patterns = patterns or TASK_PATTERNS
        self.mcp_tool_categories = self._initialize_tool_categories()
    
    def _initialize_tool_categories(self) -> Dict[str, List[str]]:
        """Initialize MCP tool categories"""
        return {
            "swarm_orchestration": [
                "swarm_init", "agent_spawn", "task_orchestrate", "swarm_monitor",
                "topology_optimize", "load_balance", "coordination_sync", 
                "swarm_scale", "swarm_destroy"
            ],
            "neural_cognitive": [
                "neural_train", "neural_predict", "pattern_recognize", 
                "cognitive_analyze", "learning_adapt", "neural_compress",
                "ensemble_create", "transfer_learn", "neural_explain"
            ],
            "memory_management": [
                "memory_usage", "memory_search", "memory_persist", 
                "memory_namespace", "memory_backup", "memory_restore",
                "memory_compress", "memory_sync", "memory_analytics"
            ],
            "performance_monitoring": [
                "performance_report", "bottleneck_analyze", "token_usage",
                "benchmark_run", "metrics_collect", "trend_analysis",
                "health_check", "diagnostic_run", "usage_stats"
            ],
            "workflow_automation": [
                "workflow_create", "workflow_execute", "workflow_export",
                "automation_setup", "pipeline_create", "scheduler_manage",
                "trigger_setup", "batch_process", "parallel_execute"
            ],
            "github_integration": [
                "github_repo_analyze", "github_pr_manage", "github_issue_track",
                "github_release_coord", "github_workflow_auto", "github_code_review"
            ],
            "dynamic_agents": [
                "daa_agent_create", "daa_capability_match", "daa_resource_alloc",
                "daa_lifecycle_manage", "daa_communication", "daa_consensus"
            ],
            "system_security": [
                "security_scan", "backup_create", "restore_system",
                "config_manage", "features_detect", "log_analysis"
            ]
        }
    
    def analyze_task_patterns(self, description: str) -> List[TaskPattern]:
        """Identify matching task patterns"""
        desc_lower = description.lower()
        matched_patterns = []
        pattern_scores = []
        
        for pattern in self.patterns:
            # Calculate match score
            keyword_score = pattern.matches_keywords(description)
            
            # Check regex patterns
            regex_score = 0
            for regex in pattern.regex_patterns:
                if re.search(regex, desc_lower, re.IGNORECASE):
                    regex_score += 2
            
            total_score = keyword_score + regex_score
            
            if total_score > 0:
                pattern_scores.append((pattern, total_score))
        
        # Sort by score and return top matches
        pattern_scores.sort(key=lambda x: x[1], reverse=True)
        matched_patterns = [p[0] for p in pattern_scores[:5]]  # Top 5 patterns
        
        return matched_patterns
    
    def calculate_complexity(self, description: str, patterns: List[TaskPattern]) -> Tuple[TaskComplexity, int]:
        """Calculate task complexity with pattern-based modifiers"""
        desc_lower = description.lower()
        base_score = 3  # Start with moderate complexity
        
        # Length-based modifier
        word_count = len(description.split())
        if word_count < 10:
            base_score -= 1
        elif word_count > 50:
            base_score += 1
        elif word_count > 100:
            base_score += 2
        
        # Technical depth indicators
        technical_indicators = [
            ("microservice", 2), ("distributed", 2), ("enterprise", 3),
            ("scale", 2), ("architecture", 2), ("integration", 1),
            ("migration", 2), ("optimization", 1), ("security", 2),
            ("real-time", 2), ("concurrent", 2), ("async", 1),
            ("machine learning", 2), ("ai", 2), ("neural", 2)
        ]
        
        for indicator, modifier in technical_indicators:
            if indicator in desc_lower:
                base_score += modifier
        
        # Apply pattern modifiers
        for pattern in patterns:
            base_score += pattern.complexity_modifier
        
        # Multiple pattern complexity
        if len(patterns) > 2:
            base_score += 1
        if len(patterns) > 4:
            base_score += 1
        
        # Check for specific complexity keywords
        if re.search(r'\b(simple|basic|trivial)\b', desc_lower):
            base_score -= 1
        if re.search(r'\b(complex|advanced|sophisticated)\b', desc_lower):
            base_score += 1
        
        # Clamp to valid range
        base_score = max(1, min(10, base_score))
        
        # Get TaskComplexity enum
        complexity = TaskComplexity.from_score(base_score)
        
        return complexity, base_score
    
    def recommend_agents(self, patterns: List[TaskPattern], 
                        complexity: TaskComplexity) -> Tuple[int, List[str]]:
        """Recommend agents based on patterns and complexity"""
        # Collect all required agents from patterns
        required_agents = set()
        for pattern in patterns:
            required_agents.update(pattern.required_agents)
        
        # Get base agent count from complexity
        base_count = complexity.agent_count
        
        # Ensure we have at least the required agents
        agent_count = max(base_count, len(required_agents))
        
        # Convert to list and ensure coordinator is first
        agent_list = list(required_agents)
        if "coordinator" in agent_list:
            agent_list.remove("coordinator")
            agent_list.insert(0, "coordinator")
        elif agent_count > 0:
            agent_list.insert(0, "coordinator")
        
        # Add additional agents based on complexity
        additional_agents = ["analyst", "monitor", "specialist", "optimizer", "researcher"]
        for agent in additional_agents:
            if len(agent_list) < agent_count and agent not in agent_list:
                agent_list.append(agent)
        
        # For very complex tasks, ensure we have enough diversity
        if complexity.score >= 8 and len(agent_list) < agent_count:
            specialized_agents = ["documenter", "reviewer", "designer"]
            for agent in specialized_agents:
                if len(agent_list) < agent_count and agent not in agent_list:
                    agent_list.append(agent)
        
        return agent_count, agent_list[:agent_count]
    
    def recommend_tools(self, patterns: List[TaskPattern], 
                       complexity: TaskComplexity, 
                       agent_roles: List[str]) -> Tuple[List[str], List[str]]:
        """Recommend MCP tools based on patterns, complexity, and agents
        
        Returns:
            Tuple of (recommended_tools, required_tools)
        """
        tool_set = set()
        required_tools = set()
        
        # Use comprehensive mappings if available
        if get_required_tools:
            # Get required tools from mapping
            required_list = get_required_tools(patterns, complexity.score, agent_roles)
            required_tools.update(required_list)
            
            # Add pattern-specific recommended tools
            for pattern in patterns:
                if pattern.name in TASK_PATTERN_TOOLS:
                    tool_info = TASK_PATTERN_TOOLS[pattern.name]
                    required_tools.update(tool_info.get("required", []))
                    tool_set.update(tool_info.get("recommended", []))
        else:
            # Fallback to original logic
            for pattern in patterns:
                tool_set.update(pattern.suggested_tools)
                
                # Mark certain pattern tools as required
                if pattern.name in ["api_development", "frontend_development", "backend_development"]:
                    required_tools.add("workflow_create")
                elif pattern.name in ["performance_optimization"]:
                    required_tools.update(["bottleneck_analyze", "performance_report"])
                elif pattern.name in ["debugging"]:
                    required_tools.update(["diagnostic_run", "log_analysis"])
                elif pattern.name in ["security_audit"]:
                    required_tools.update(["security_scan", "github_code_review"])
                elif pattern.name in ["deployment"]:
                    required_tools.update(["workflow_create", "parallel_execute"])
        
        # Add complexity-based tools
        if complexity.score >= 9:  # Enterprise level
            tool_set.update([
                "hive_mind_spawn", "neural_train", "ensemble_create",
                "daa_agent_create", "daa_consensus"
            ])
            required_tools.update(["hive_mind_spawn", "daa_agent_create"])
        elif complexity.score >= 7:  # Advanced level
            tool_set.update([
                "neural_predict", "pattern_recognize", "cognitive_analyze",
                "workflow_create", "parallel_execute"
            ])
            required_tools.add("cognitive_analyze")
        elif complexity.score >= 5:  # Intermediate level
            tool_set.update([
                "workflow_create", "memory_sync", "performance_report"
            ])
        
        # Add agent-specific tools
        agent_tool_mapping = {
            "coordinator": ["swarm_init", "task_orchestrate", "coordination_sync"],
            "researcher": ["memory_search", "pattern_recognize", "github_repo_analyze"],
            "coder": ["github_code_review", "workflow_create", "parallel_execute"],
            "tester": ["benchmark_run", "diagnostic_run", "health_check"],
            "optimizer": ["bottleneck_analyze", "performance_report", "neural_predict"],
            "analyst": ["trend_analysis", "memory_analytics", "cognitive_analyze"],
            "architect": ["github_repo_analyze", "pattern_recognize", "workflow_create"],
            "reviewer": ["security_scan", "github_code_review", "log_analysis"],
            "monitor": ["health_check", "metrics_collect", "usage_stats"],
            "specialist": ["daa_capability_match", "features_detect", "config_manage"]
        }
        
        for agent in agent_roles:
            if agent in agent_tool_mapping:
                tool_set.update(agent_tool_mapping[agent])
        
        # Always include basic orchestration tools for non-trivial tasks
        if complexity.score > 3:
            required_tools.update(["swarm_init", "agent_spawn", "task_orchestrate"])
        
        # Memory usage is always required for context
        required_tools.add("memory_usage")
        
        # Merge required into recommended
        tool_set.update(required_tools)
        
        # Limit tools to prevent overwhelming output
        tool_list = sorted(list(tool_set))
        required_list = sorted(list(required_tools))
        
        return tool_list[:25], required_list  # Increased limit for more tools
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Complete prompt analysis"""
        # Identify patterns
        patterns = self.analyze_task_patterns(prompt)
        
        # Calculate complexity
        complexity, complexity_score = self.calculate_complexity(prompt, patterns)
        
        # Get agent recommendations
        agent_count, agent_roles = self.recommend_agents(patterns, complexity)
        
        # Get tool recommendations
        recommended_tools, required_tools = self.recommend_tools(patterns, complexity, agent_roles)
        
        # Extract technologies
        tech_involved = self._extract_technologies(prompt)
        
        return {
            "patterns": patterns,
            "complexity": complexity,
            "complexity_score": complexity_score,
            "agent_count": agent_count,
            "agent_roles": agent_roles,
            "mcp_tools": recommended_tools,
            "required_mcp_tools": required_tools,
            "tech_involved": tech_involved
        }
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract technology mentions from text"""
        text_lower = text.lower()
        
        tech_patterns = {
            "Python": r'\b(python|py|django|flask|fastapi)\b',
            "JavaScript": r'\b(javascript|js|node|react|vue|angular)\b',
            "TypeScript": r'\b(typescript|ts)\b',
            "Database": r'\b(database|sql|postgres|mysql|mongodb|redis)\b',
            "API": r'\b(api|rest|graphql|endpoint)\b',
            "Cloud": r'\b(aws|azure|gcp|cloud|serverless)\b',
            "Docker": r'\b(docker|container|kubernetes|k8s)\b',
            "Git": r'\b(git|github|gitlab|version control)\b',
            "Testing": r'\b(test|testing|jest|pytest|mocha)\b',
            "CI/CD": r'\b(ci|cd|jenkins|github actions|pipeline)\b'
        }
        
        technologies = []
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, text_lower):
                technologies.append(tech)
        
        return technologies