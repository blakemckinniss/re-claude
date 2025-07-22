#!/usr/bin/env python3
"""
Claude Code Hook Router - Central Python-based hook management system
Replaces multiple shell scripts with a single, maintainable Python router.
"""

import json
import sys
import os
import subprocess
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class HookEvent(Enum):
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    USER_PROMPT_SUBMIT = "UserPromptSubmit"
    NOTIFICATION = "Notification"
    STOP = "Stop"
    SUBAGENT_STOP = "SubagentStop"

class Decision(Enum):
    APPROVE = "approve"
    BLOCK = "block"

@dataclass
class HookInput:
    session_id: str
    transcript_path: str
    hook_event_name: str
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Optional[str] = None

@dataclass
class HookResponse:
    decision: Optional[str] = None
    reason: Optional[str] = None
    continue_execution: bool = True
    stop_reason: Optional[str] = None
    suppress_output: bool = False

class ClaudeFlowIntegration:
    """Integration with claude-flow commands"""
    
    @staticmethod
    def run_command(cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """Run claude-flow command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=capture_output, 
                text=True, 
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    @staticmethod
    def memory_store(key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Store value in claude-flow memory"""
        cmd = ["npx", "claude-flow@alpha", "memory", "store", key, value]
        if ttl:
            cmd.extend(["--ttl", str(ttl)])
        exit_code, _, _ = ClaudeFlowIntegration.run_command(cmd)
        return exit_code == 0
    
    @staticmethod
    def memory_query(key: str) -> Optional[str]:
        """Query value from claude-flow memory"""
        cmd = ["npx", "claude-flow@alpha", "memory", "query", key]
        exit_code, stdout, _ = ClaudeFlowIntegration.run_command(cmd)
        if exit_code == 0:
            try:
                data = json.loads(stdout)
                return data.get("value")
            except json.JSONDecodeError:
                return None
        return None
    
    @staticmethod
    def swarm_init(topology: str = "mesh", max_agents: int = 5) -> bool:
        """Initialize swarm with specified topology"""
        cmd = [
            "npx", "claude-flow@alpha", "coordination", "swarm-init",
            "--topology", topology,
            "--max-agents", str(max_agents),
            "--strategy", "adaptive"
        ]
        exit_code, _, _ = ClaudeFlowIntegration.run_command(cmd)
        return exit_code == 0
    
    @staticmethod
    def agent_spawn(agent_type: str, name: str) -> bool:
        """Spawn a new agent"""
        cmd = [
            "npx", "claude-flow@alpha", "coordination", "agent-spawn",
            "--type", agent_type,
            "--name", name,
            "--capabilities", "task-specific"
        ]
        exit_code, _, _ = ClaudeFlowIntegration.run_command(cmd)
        return exit_code == 0

class TaskAnalyzer:
    """Analyzes tasks for complexity and agent requirements"""
    
    COMPLEXITY_KEYWORDS = {
        "high": ["complex", "enterprise", "distributed", "microservice", "scale", "architect"],
        "low": ["simple", "basic", "fix", "update", "modify"],
        "api": ["api", "endpoint", "rest", "graphql"],
        "database": ["database", "db", "sql", "migration", "schema"],
        "auth": ["auth", "authentication", "authorization", "security"],
        "frontend": ["frontend", "ui", "react", "vue", "angular"],
        "backend": ["backend", "server", "service"],
        "test": ["test", "testing", "qa", "coverage"],
        "deploy": ["deploy", "deployment", "ci", "cd"],
        "performance": ["performance", "optimize", "speed", "bottleneck"]
    }
    
    @staticmethod
    def analyze_complexity(description: str) -> Tuple[str, int]:
        """Analyze task complexity and suggest agent count"""
        desc_lower = description.lower()
        
        # Count technical keywords
        keyword_count = 0
        for category, keywords in TaskAnalyzer.COMPLEXITY_KEYWORDS.items():
            if category in ["high", "low"]:
                continue
            keyword_count += sum(1 for keyword in keywords if keyword in desc_lower)
        
        # Determine complexity
        if any(keyword in desc_lower for keyword in TaskAnalyzer.COMPLEXITY_KEYWORDS["low"]):
            return "low", 3
        elif any(keyword in desc_lower for keyword in TaskAnalyzer.COMPLEXITY_KEYWORDS["high"]):
            return "high", 8
        elif keyword_count > 5:
            return "high", 10
        elif keyword_count <= 2:
            return "low", 4
        else:
            return "medium", 5
    
    @staticmethod
    def suggest_agent_types(description: str) -> List[str]:
        """Suggest agent types based on task description"""
        desc_lower = description.lower()
        agent_types = []
        
        # Always include coordinator for non-trivial tasks
        complexity, _ = TaskAnalyzer.analyze_complexity(description)
        if complexity != "low":
            agent_types.append("coordinator")
        
        # Task-specific agents
        if re.search(r"(research|analyze|investigate)", desc_lower):
            agent_types.append("researcher")
        if re.search(r"(code|implement|develop|build)", desc_lower):
            agent_types.append("coder")
        if re.search(r"(test|qa|quality|coverage)", desc_lower):
            agent_types.append("tester")
        if re.search(r"(design|architect|structure)", desc_lower):
            agent_types.append("architect")
        if re.search(r"(review|audit|security)", desc_lower):
            agent_types.append("reviewer")
        if re.search(r"(optimize|performance|speed)", desc_lower):
            agent_types.append("optimizer")
        if re.search(r"(document|docs|readme)", desc_lower):
            agent_types.append("documenter")
        
        # Default balanced team if no specific types detected
        if not agent_types:
            agent_types = ["coordinator", "researcher", "coder", "analyst", "tester"]
        
        return agent_types
    
    @staticmethod
    def suggest_topology(description: str) -> str:
        """Suggest optimal topology based on task type"""
        desc_lower = description.lower()
        
        if re.search(r"(coordinate|manage|orchestrate)", desc_lower):
            return "hierarchical"
        elif re.search(r"(pipeline|sequence|flow)", desc_lower):
            return "ring"
        elif re.search(r"(central|hub|core)", desc_lower):
            return "star"
        else:
            return "mesh"

class HookRouter:
    """Main hook router that handles all hook events"""
    
    def __init__(self):
        self.cf = ClaudeFlowIntegration()
        self.analyzer = TaskAnalyzer()
    
    def route_hook(self, hook_input: HookInput) -> HookResponse:
        """Route hook to appropriate handler based on event and tool"""
        try:
            event = HookEvent(hook_input.hook_event_name)
            
            if event == HookEvent.PRE_TOOL_USE:
                return self._handle_pre_tool_use(hook_input)
            elif event == HookEvent.POST_TOOL_USE:
                return self._handle_post_tool_use(hook_input)
            elif event == HookEvent.USER_PROMPT_SUBMIT:
                return self._handle_user_prompt_submit(hook_input)
            elif event == HookEvent.STOP:
                return self._handle_stop(hook_input)
            elif event == HookEvent.SUBAGENT_STOP:
                return self._handle_subagent_stop(hook_input)
            elif event == HookEvent.NOTIFICATION:
                return self._handle_notification(hook_input)
            else:
                return HookResponse(decision=Decision.APPROVE.value)
                
        except Exception as e:
            self._log_error(f"Hook routing error: {e}")
            return HookResponse(decision=Decision.APPROVE.value)
    
    def _handle_pre_tool_use(self, hook_input: HookInput) -> HookResponse:
        """Handle PreToolUse events"""
        tool_name = hook_input.tool_name
        
        if tool_name == "Task":
            return self._handle_pre_task(hook_input)
        elif tool_name == "TodoWrite":
            return self._handle_pre_todo_write(hook_input)
        elif tool_name == "Bash":
            return self._handle_pre_bash(hook_input)
        elif tool_name in ["Write", "Edit", "MultiEdit"]:
            return self._handle_pre_file_operation(hook_input)
        elif tool_name in ["Read", "Grep", "Glob", "LS"]:
            return self._handle_pre_read_operation(hook_input)
        elif tool_name.startswith("mcp__claude-flow__"):
            return self._handle_pre_mcp_operation(hook_input)
        
        return HookResponse(decision=Decision.APPROVE.value)
    
    def _handle_post_tool_use(self, hook_input: HookInput) -> HookResponse:
        """Handle PostToolUse events"""
        tool_name = hook_input.tool_name
        
        if tool_name == "Task":
            return self._handle_post_task(hook_input)
        elif tool_name in ["Edit", "MultiEdit"]:
            return self._handle_post_edit(hook_input)
        elif tool_name == "TodoWrite":
            return self._handle_post_todo_write(hook_input)
        elif tool_name == "Bash":
            return self._handle_post_bash(hook_input)
        elif tool_name in ["Write", "Edit", "MultiEdit"]:
            return self._handle_post_file_operation(hook_input)
        elif tool_name in ["Read", "Grep", "Glob", "LS"]:
            return self._handle_post_read_operation(hook_input)
        elif tool_name == "mcp__claude-flow__swarm_init":
            return self._handle_post_swarm_init(hook_input)
        elif tool_name == "mcp__claude-flow__agent_spawn":
            return self._handle_post_agent_spawn(hook_input)
        elif tool_name == "mcp__claude-flow__memory_usage":
            return self._handle_post_memory_operation(hook_input)
        
        return HookResponse()
    
    def _handle_pre_task(self, hook_input: HookInput) -> HookResponse:
        """Enhanced pre-task handler with auto-spawning and optimization"""
        self._log_info("🎯 Enhanced Pre-Task Analysis...")
        
        task_desc = hook_input.tool_input.get("description", "")
        session_id = hook_input.session_id
        auto_spawn = hook_input.tool_input.get("auto_spawn_agents", True)
        timestamp = int(time.time())
        
        # Analyze task complexity
        self._log_info("🧠 Analyzing task complexity...")
        complexity, suggested_agents = self.analyzer.analyze_complexity(task_desc)
        
        # Check if swarm is initialized
        swarm_key = f"swarm-initialized-{session_id}"
        swarm_init = self.cf.memory_query(swarm_key) == "true"
        
        if not swarm_init and auto_spawn:
            self._log_info("🐝 Auto-initializing swarm for task...")
            topology = self.analyzer.suggest_topology(task_desc)
            
            self._log_info(f"   Selected topology: {topology}")
            self._log_info(f"   Suggested agents: {suggested_agents}")
            
            if self.cf.swarm_init(topology, suggested_agents):
                self.cf.memory_store(swarm_key, "true", 3600)
                swarm_init = True
        
        # Auto-spawn agents based on task analysis
        if auto_spawn and swarm_init:
            self._log_info("🤖 Auto-spawning specialized agents...")
            agent_types = self.analyzer.suggest_agent_types(task_desc)
            
            for agent_type in agent_types:
                self._log_info(f"   Spawning {agent_type} agent...")
                agent_name = f"Auto-{agent_type}-{timestamp}"
                self.cf.agent_spawn(agent_type, agent_name)
            
            self.cf.memory_store(f"swarm/{session_id}/agent-count", str(len(agent_types)))
        
        # Store task metadata
        task_metadata = {
            "description": task_desc,
            "complexity": complexity,
            "suggested_agents": suggested_agents,
            "auto_spawned": auto_spawn,
            "timestamp": timestamp
        }
        
        self.cf.memory_store(f"tasks/{session_id}/current", json.dumps(task_metadata))
        self.cf.memory_store(f"tasks/{session_id}/complexity", complexity)
        
        # Generate execution plan
        self._log_execution_plan(task_desc, complexity, suggested_agents)
        
        return HookResponse(decision=Decision.APPROVE.value)
    
    def _handle_pre_todo_write(self, hook_input: HookInput) -> HookResponse:
        """Handle batch TODO enforcement"""
        # Implementation for batch TODO enforcement
        return HookResponse(decision=Decision.APPROVE.value)
    
    def _handle_pre_bash(self, hook_input: HookInput) -> HookResponse:
        """Handle pre-bash command validation"""
        # Implementation for bash command validation
        return HookResponse(decision=Decision.APPROVE.value)
    
    def _handle_pre_file_operation(self, hook_input: HookInput) -> HookResponse:
        """Handle pre-file operation validation"""
        file_path = hook_input.tool_input.get("file_path", "")
        
        # Block modifications to sensitive files
        sensitive_patterns = [".env", "secrets.json", ".git/"]
        for pattern in sensitive_patterns:
            if pattern in file_path:
                return HookResponse(
                    decision=Decision.BLOCK.value,
                    reason=f"Cannot modify sensitive file: {file_path}"
                )
        
        return HookResponse(decision=Decision.APPROVE.value)
    
    def _handle_pre_read_operation(self, hook_input: HookInput) -> HookResponse:
        """Handle pre-read operation validation"""
        return HookResponse(decision=Decision.APPROVE.value)
    
    def _handle_pre_mcp_operation(self, hook_input: HookInput) -> HookResponse:
        """Handle MCP coordination validation"""
        return HookResponse(decision=Decision.APPROVE.value)
    
    def _handle_post_task(self, hook_input: HookInput) -> HookResponse:
        """Handle post-task coordination"""
        return HookResponse()
    
    def _handle_post_edit(self, hook_input: HookInput) -> HookResponse:
        """Handle post-edit operations like formatting"""
        file_path = hook_input.tool_input.get("file_path", "")
        
        # Auto-format based on file extension (only if file exists)
        if file_path and os.path.exists(file_path):
            try:
                if file_path.endswith('.py'):
                    result = subprocess.run(["black", file_path], capture_output=True, text=True)
                    if result.returncode == 0:
                        self._log_info(f"Formatted Python file: {file_path}")
                    else:
                        self._log_info(f"Black formatting skipped for: {file_path}")
                elif file_path.endswith(('.js', '.ts')):
                    result = subprocess.run(["npx", "prettier", "--write", file_path], capture_output=True, text=True)
                    if result.returncode == 0:
                        self._log_info(f"Formatted JS/TS file: {file_path}")
                    else:
                        self._log_info(f"Prettier formatting skipped for: {file_path}")
            except FileNotFoundError:
                # Formatter not available, skip silently
                pass
            except Exception as e:
                self._log_info(f"Formatting skipped for {file_path}: {str(e)}")
        
        return HookResponse()
    
    def _handle_post_todo_write(self, hook_input: HookInput) -> HookResponse:
        """Handle post-todo tracking"""
        return HookResponse()
    
    def _handle_post_bash(self, hook_input: HookInput) -> HookResponse:
        """Handle post-bash tracking"""
        return HookResponse()
    
    def _handle_post_file_operation(self, hook_input: HookInput) -> HookResponse:
        """Handle post-file operation tasks"""
        return HookResponse()
    
    def _handle_post_read_operation(self, hook_input: HookInput) -> HookResponse:
        """Handle post-read operation tasks"""
        return HookResponse()
    
    def _handle_post_swarm_init(self, hook_input: HookInput) -> HookResponse:
        """Handle post-swarm initialization"""
        return HookResponse()
    
    def _handle_post_agent_spawn(self, hook_input: HookInput) -> HookResponse:
        """Handle post-agent spawn tasks"""
        return HookResponse()
    
    def _handle_post_memory_operation(self, hook_input: HookInput) -> HookResponse:
        """Handle post-memory operation tasks"""
        return HookResponse()
    
    def _handle_user_prompt_submit(self, hook_input: HookInput) -> HookResponse:
        """Handle user prompt submission"""
        return HookResponse()
    
    def _handle_stop(self, hook_input: HookInput) -> HookResponse:
        """Handle session end coordination"""
        return HookResponse()
    
    def _handle_subagent_stop(self, hook_input: HookInput) -> HookResponse:
        """Handle subagent stop coordination"""
        return HookResponse()
    
    def _handle_notification(self, hook_input: HookInput) -> HookResponse:
        """Handle notification broadcasting"""
        return HookResponse()
    
    def _log_info(self, message: str):
        """Log info message to stderr"""
        print(message, file=sys.stderr)
    
    def _log_error(self, message: str):
        """Log error message to stderr"""
        print(f"ERROR: {message}", file=sys.stderr)
    
    def _log_execution_plan(self, task_desc: str, complexity: str, suggested_agents: int):
        """Log execution plan"""
        self._log_info("")
        self._log_info("📋 TASK EXECUTION PLAN")
        self._log_info("═══════════════════════════════════════════")
        self._log_info(f"📝 Task:         {task_desc[:50]}...")
        self._log_info(f"🎯 Complexity:   {complexity}")
        self._log_info(f"👥 Agents:       {suggested_agents} suggested")
        self._log_info("═══════════════════════════════════════════")

def main():
    """Main entry point for the hook router"""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Parse hook input
        hook_input = HookInput(
            session_id=input_data.get("session_id", ""),
            transcript_path=input_data.get("transcript_path", ""),
            hook_event_name=input_data.get("hook_event_name", ""),
            tool_name=input_data.get("tool_name", ""),
            tool_input=input_data.get("tool_input", {}),
            tool_output=input_data.get("tool_output")
        )
        
        # Route the hook
        router = HookRouter()
        response = router.route_hook(hook_input)
        
        # Output response
        output = {}
        if response.decision:
            output["decision"] = response.decision
        if response.reason:
            output["reason"] = response.reason
        if not response.continue_execution:
            output["continue"] = False
        if response.stop_reason:
            output["stopReason"] = response.stop_reason
        if response.suppress_output:
            output["suppressOutput"] = True
        
        print(json.dumps(output))
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()