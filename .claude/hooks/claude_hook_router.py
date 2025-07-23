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

# Add local memory import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory.local_memory import LocalMemoryStore
from mcp_tool_mappings import get_required_tools, TASK_PATTERN_TOOLS

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
    """Integration with claude-flow commands with local memory fallback"""
    
    def __init__(self):
        self.local_memory = LocalMemoryStore()
    
    def run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
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
    
    def memory_store(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Store value in claude-flow memory with local fallback"""
        # Try claude-flow first
        cmd = ["npx", "claude-flow@alpha", "memory", "store", key, value]
        if ttl:
            cmd.extend(["--ttl", str(ttl)])
        exit_code, _, _ = self.run_command(cmd)
        
        # Use local memory as fallback or primary
        self.local_memory.store(key, value, ttl)
        
        return exit_code == 0 or True  # Always succeed with local fallback
    
    def memory_query(self, key: str) -> Optional[str]:
        """Query value from claude-flow memory with local fallback"""
        # Try local memory first (faster)
        local_value = self.local_memory.query(key)
        if local_value:
            return local_value
        
        # Try claude-flow
        cmd = ["npx", "claude-flow@alpha", "memory", "query", key]
        exit_code, stdout, _ = self.run_command(cmd)
        if exit_code == 0:
            try:
                data = json.loads(stdout)
                value = data.get("value")
                if value:
                    # Cache in local memory
                    self.local_memory.store(key, value)
                return value
            except json.JSONDecodeError:
                pass
        
        return None
    
    def swarm_init(self, topology: str = "mesh", max_agents: int = 5) -> bool:
        """Initialize swarm with specified topology"""
        cmd = [
            "npx", "claude-flow@alpha", "coordination", "swarm-init",
            "--topology", topology,
            "--max-agents", str(max_agents),
            "--strategy", "adaptive"
        ]
        exit_code, _, _ = self.run_command(cmd)
        return exit_code == 0
    
    def agent_spawn(self, agent_type: str, name: str) -> bool:
        """Spawn a new agent"""
        cmd = [
            "npx", "claude-flow@alpha", "coordination", "agent-spawn",
            "--type", agent_type,
            "--name", name,
            "--capabilities", "task-specific"
        ]
        exit_code, _, _ = self.run_command(cmd)
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
        # Session tracking for parallel enforcement
        self.current_message_tools = {}
        # Load enforcement level from config
        self.enforcement_level = self._load_enforcement_level()
    
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
        
        # Check if required MCP tools are being skipped
        skip_validation = self._check_mcp_tools_skip(session_id, "Task")
        if skip_validation:
            return skip_validation
        
        # Check for sequential Task spawning
        message_key = f"session/{session_id}/current_message_tools"
        current_tools = json.loads(self.cf.memory_query(message_key) or "[]")
        task_count = current_tools.count("Task")
        
        if task_count > 0 and self.enforcement_level in ["enforce", "strict"]:
            # Check if this is part of a batch or sequential
            last_task_time = self.cf.memory_query(f"session/{session_id}/last_task_time")
            if last_task_time and (timestamp - int(last_task_time or 0)) > 2:
                return self._block_with_visual_guidance(
                    "SEQUENTIAL AGENT SPAWNING DETECTED",
                    "Spawn ALL agents in ONE message using parallel Task calls!",
                    "Multiple Task calls in a single message",
                    "Sequential Task calls across messages"
                )
        
        # Store task timing
        self.cf.memory_store(f"session/{session_id}/last_task_time", str(timestamp), 60)
        
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
        todos = hook_input.tool_input.get("todos", [])
        session_id = hook_input.session_id
        
        # Check if required MCP tools are being skipped
        skip_validation = self._check_mcp_tools_skip(session_id, "TodoWrite")
        if skip_validation:
            return skip_validation
        
        # Check for sequential TodoWrite calls
        message_key = f"session/{session_id}/current_message_tools"
        current_tools = json.loads(self.cf.memory_query(message_key) or "[]")
        
        if "TodoWrite" in current_tools:
            return self._block_with_visual_guidance(
                "SEQUENTIAL TodoWrite DETECTED",
                "Batch ALL todos in ONE TodoWrite call!",
                "TodoWrite with 5-10+ todos in a single call",
                "Multiple TodoWrite calls in sequence"
            )
        
        # Enforce minimum batch size
        if len(todos) < 5:
            if self.enforcement_level in ["enforce", "strict"]:
                return HookResponse(
                    decision=Decision.BLOCK.value,
                    reason="❌ TodoWrite must include at least 5-10 todos in a single call. Batch all todos together!"
                )
            else:
                self._log_info("⚠️ Warning: TodoWrite should include 5-10+ todos for optimal batching")
        
        # Check for proper status distribution
        statuses = [todo.get("status") for todo in todos]
        if len(todos) >= 5 and all(s == "pending" for s in statuses):
            self._log_info("💡 Tip: Include mixed statuses (completed, in_progress, pending) to show progress")
        
        # Track tool usage
        current_tools.append("TodoWrite")
        self.cf.memory_store(message_key, json.dumps(current_tools), 60)
        
        return HookResponse(decision=Decision.APPROVE.value)
    
    def _handle_pre_bash(self, hook_input: HookInput) -> HookResponse:
        """Handle pre-bash command validation"""
        command = hook_input.tool_input.get("command", "")
        session_id = hook_input.session_id
        
        # Track for parallel enforcement
        message_key = f"session/{session_id}/current_message_tools"
        current_tools = json.loads(self.cf.memory_query(message_key) or "[]")
        
        # Check for dangerous commands
        dangerous_patterns = [
            r"rm\s+-rf\s+/",
            r"curl.*\|\s*bash",
            r"wget.*\|\s*sh",
            r"sudo\s+rm",
            r":(){\s*:\|:\s*&\s*};"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return HookResponse(
                    decision=Decision.BLOCK.value,
                    reason=f"Dangerous command pattern detected: {pattern}"
                )
        
        # Track tool usage
        current_tools.append("Bash")
        self.cf.memory_store(message_key, json.dumps(current_tools), 60)
        
        return HookResponse(decision=Decision.APPROVE.value)
    
    def _handle_pre_file_operation(self, hook_input: HookInput) -> HookResponse:
        """Handle pre-file operation validation"""
        file_path = hook_input.tool_input.get("file_path", "")
        session_id = hook_input.session_id
        tool_name = hook_input.tool_name
        
        # Check if required MCP tools are being skipped (for write operations)
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            skip_validation = self._check_mcp_tools_skip(session_id, tool_name)
            if skip_validation:
                return skip_validation
        
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
        tool_name = hook_input.tool_name
        session_id = hook_input.session_id
        
        # Special handling for swarm_init
        if tool_name == "mcp__claude-flow__swarm_init":
            # Mark that swarm is being initialized
            self.cf.memory_store(
                f"session/{session_id}/swarm_init_pending",
                "true",
                60
            )
        
        # Track MCP tool usage
        message_key = f"session/{session_id}/current_message_tools"
        current_tools = json.loads(self.cf.memory_query(message_key) or "[]")
        current_tools.append(tool_name)
        self.cf.memory_store(message_key, json.dumps(current_tools), 60)
        
        # Track specific MCP tools used (for required tool validation)
        mcp_tools_key = f"session/{session_id}/mcp_tools_used"
        mcp_tools_used = json.loads(self.cf.memory_query(mcp_tools_key) or "[]")
        # Extract tool name without prefix
        clean_tool_name = tool_name.replace("mcp__claude-flow__", "")
        if clean_tool_name not in mcp_tools_used:
            mcp_tools_used.append(clean_tool_name)
        self.cf.memory_store(mcp_tools_key, json.dumps(mcp_tools_used), 3600)
        
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
        session_id = hook_input.session_id
        # Mark swarm as initialized
        self.cf.memory_store(
            f"session/{session_id}/swarm_initialized",
            "true",
            3600
        )
        # Clear pending flag
        self.cf.memory_store(
            f"session/{session_id}/swarm_init_pending",
            "false",
            60
        )
        return HookResponse()
    
    def _handle_post_agent_spawn(self, hook_input: HookInput) -> HookResponse:
        """Handle post-agent spawn tasks"""
        return HookResponse()
    
    def _handle_post_memory_operation(self, hook_input: HookInput) -> HookResponse:
        """Handle post-memory operation tasks"""
        return HookResponse()
    
    def _handle_user_prompt_submit(self, hook_input: HookInput) -> HookResponse:
        """Handle user prompt submission with MCP injection"""
        prompt = hook_input.tool_input.get("prompt", "")
        session_id = hook_input.session_id
        
        # Reset message tracking for new prompt
        self._reset_message_tracking(session_id)
        
        # Analyze complexity for MCP injection
        complexity, agent_count = self.analyzer.analyze_complexity(prompt)
        complexity_score = self._get_complexity_score(complexity)
        
        # Get full task analysis including required tools
        full_analysis = self.analyzer.analyze_prompt(prompt)
        required_tools = full_analysis.get('required_mcp_tools', [])
        
        # Auto-inject MCP requirements for complex tasks
        if complexity_score >= 4 and self.enforcement_level in ["enforce", "strict"]:
            enhanced_prompt = self._inject_mcp_requirements(prompt, complexity, agent_count, required_tools)
            hook_input.tool_input["prompt"] = enhanced_prompt
            
            # Store enforcement metadata including required tools
            self.cf.memory_store(
                f"session/{session_id}/enforcement_active", 
                "true", 
                3600
            )
            self.cf.memory_store(
                f"session/{session_id}/required_mcp_tools",
                json.dumps(required_tools),
                3600
            )
        
        return HookResponse()
    
    def _handle_stop(self, hook_input: HookInput) -> HookResponse:
        """Handle session end coordination"""
        return HookResponse()
    
    def _handle_subagent_stop(self, hook_input: HookInput) -> HookResponse:
        """Handle subagent stop coordination"""
        return HookResponse()
    
    def _handle_notification(self, hook_input: HookInput) -> HookResponse:
        """Handle notification broadcasting"""
        # Reset message tracking on certain notifications
        notification_type = hook_input.tool_input.get("type", "")
        session_id = hook_input.session_id
        
        if notification_type in ["message_complete", "prompt_processed"]:
            # Validate MCP tool usage before resetting
            self._validate_mcp_tool_usage(session_id)
            self._reset_message_tracking(session_id)
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
    
    def _block_with_visual_guidance(self, violation: str, fix: str, 
                                   correct: str, incorrect: str) -> HookResponse:
        """Block with clear visual guidance"""
        guidance = f"""
❌ CLAUDE-FLOW VIOLATION DETECTED
═══════════════════════════════════════════════

{violation}

✅ CORRECT PATTERN:
┌─ Single Message ─────────────────────────────┐
│ • mcp__claude-flow__swarm_init               │
│ • Task (Agent 1) + Task (Agent 2) + Task (3) │
│ • TodoWrite (10+ todos)                      │
│ • Read (multiple files)                      │
└──────────────────────────────────────────────┘

❌ YOUR PATTERN: {incorrect}

🔧 FIX: {fix}

⚡ ENFORCEMENT LEVEL: {self.enforcement_level.upper()}
"""
        
        return HookResponse(
            decision=Decision.BLOCK.value,
            reason=guidance
        )
    
    def _reset_message_tracking(self, session_id: str):
        """Reset tool tracking for new message"""
        message_key = f"session/{session_id}/current_message_tools"
        self.cf.memory_store(message_key, "[]", 60)

    def _get_complexity_score(self, complexity: str) -> int:
        """Convert complexity string to numeric score"""
        scores = {"low": 3, "medium": 5, "high": 8}
        return scores.get(complexity, 5)
    
    def _inject_mcp_requirements(self, prompt: str, complexity: str, agent_count: int, required_tools: List[str] = None) -> str:
        """Inject MCP requirements into prompt"""
        topology = self.analyzer.suggest_topology(prompt)
        required_tools = required_tools or []
        
        # Check for sequential patterns and rewrite if needed
        rewritten_prompt = self._rewrite_for_compliance(prompt)
        
        injection = f"""
{rewritten_prompt}

[🔥 MCP ENFORCEMENT - {complexity.upper()} COMPLEXITY]
⚡ MANDATORY PARALLEL EXECUTION:
1. Initialize: mcp__claude-flow__swarm_init(topology="{topology}", maxAgents={agent_count})
2. Spawn ALL {agent_count} agents in ONE message using parallel Task calls
3. Create TodoWrite with 8-12 items in ONE call
4. Batch ALL file operations together
5. Use mcp__claude-flow__memory_usage for context storage"""
        
        # Add required MCP tools section
        if required_tools:
            injection += "\n\n🔧 REQUIRED MCP TOOLS (MUST USE):"
            for tool in required_tools[:10]:  # Limit to prevent overwhelming
                injection += f"\n• mcp__claude-flow__{tool}"
            if len(required_tools) > 10:
                injection += f"\n• ... (+{len(required_tools) - 10} more required tools)"
        
        injection += "\n\n⛔ VIOLATIONS WILL BE BLOCKED! Execute ALL operations in ONE message."
        
        return injection
    
    def _rewrite_for_compliance(self, prompt: str) -> str:
        """Rewrite prompts to be claude-flow compliant"""
        # Detect sequential patterns
        sequential_patterns = [
            r"\bthen\b",
            r"\bafter that\b",
            r"\bfollowed by\b",
            r"\bnext\b",
            r"\bstep by step\b",
            r"\bone by one\b",
            r"\bsequentially\b"
        ]
        
        has_sequential = any(re.search(pattern, prompt, re.IGNORECASE) for pattern in sequential_patterns)
        
        if has_sequential and self.enforcement_level in ["enforce", "strict"]:
            # Add parallel execution note
            return f"""{prompt}

[🔄 REWRITTEN FOR PARALLEL EXECUTION]
Execute ALL operations concurrently:
• Initialize swarm with appropriate topology
• Spawn ALL required agents in parallel
• Create complete todo list (5-10+ items)
• Read ALL necessary files simultaneously
• Store decisions in memory for persistence
"""
        
        return prompt
    
    def _is_complex_task(self, prompt: str) -> bool:
        """Check if task requires MCP coordination"""
        complexity, _ = self.analyzer.analyze_complexity(prompt)
        return self._get_complexity_score(complexity) >= 4
    
    def _load_enforcement_level(self) -> str:
        """Load enforcement level from settings.json"""
        try:
            settings_path = Path.home() / ".claude" / "settings.json"
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    return settings.get("claude_flow_enforcement", "enforce")
        except Exception:
            pass
        return "enforce"  # Default to enforce
    
    def _validate_mcp_tool_usage(self, session_id: str) -> None:
        """Validate that required MCP tools were actually used"""
        # Check if enforcement is active for this session
        enforcement_active = self.cf.memory_query(f"session/{session_id}/enforcement_active") == "true"
        if not enforcement_active:
            return
        
        # Get required tools
        required_tools_json = self.cf.memory_query(f"session/{session_id}/required_mcp_tools")
        if not required_tools_json:
            return
        
        try:
            required_tools = json.loads(required_tools_json)
            if not required_tools:
                return
        except json.JSONDecodeError:
            return
        
        # Get actually used MCP tools
        used_tools_json = self.cf.memory_query(f"session/{session_id}/mcp_tools_used")
        used_tools = json.loads(used_tools_json) if used_tools_json else []
        
        # Find missing required tools
        missing_tools = [tool for tool in required_tools if tool not in used_tools]
        
        if missing_tools and self.enforcement_level in ["enforce", "strict"]:
            # Generate validation report
            self._generate_mcp_validation_report(required_tools, used_tools, missing_tools)
    
    def _generate_mcp_validation_report(self, required: List[str], used: List[str], missing: List[str]) -> None:
        """Generate MCP tool usage validation report"""
        report = f"""
🔍 MCP TOOL USAGE VALIDATION
═══════════════════════════════════════════════

📋 Required MCP Tools: {len(required)}
✅ Used MCP Tools: {len(used)}
❌ Missing Required Tools: {len(missing)}

⚠️ MISSING REQUIRED TOOLS:"""
        
        for tool in missing[:10]:  # Limit display
            report += f"\n   ❌ mcp__claude-flow__{tool}"
        
        if len(missing) > 10:
            report += f"\n   ... (+{len(missing) - 10} more missing tools)"
        
        report += "\n\n✅ TOOLS THAT WERE USED:"
        for tool in used[:5]:  # Show some that were used
            report += f"\n   ✓ mcp__claude-flow__{tool}"
        
        if len(used) > 5:
            report += f"\n   ... (+{len(used) - 5} more used tools)"
        
        report += f"""

📊 COMPLIANCE SCORE: {(len(used) / len(required) * 100):.1f}%

💡 RECOMMENDATION: Review and use the missing required tools for complete task execution.
These tools were identified as MANDATORY for your task complexity and patterns.

⚡ ENFORCEMENT LEVEL: {self.enforcement_level.upper()}
"""
        
        # Log the validation report
        self._log_info(report)
        
        # Store validation results for metrics
        validation_result = {
            "timestamp": int(time.time()),
            "required_count": len(required),
            "used_count": len(used),
            "missing_count": len(missing),
            "compliance_score": len(used) / len(required) if required else 1.0,
            "missing_tools": missing
        }
        
        # Store validation metrics
        metrics_key = f"session/{self.cf.memory_query('current_session_id') or 'unknown'}/mcp_validation_metrics"
        self.cf.memory_store(metrics_key, json.dumps(validation_result), 3600)
    
    def _check_mcp_tools_skip(self, session_id: str, current_tool: str) -> Optional[HookResponse]:
        """Check if required MCP tools are being skipped in favor of other operations"""
        # Only check if enforcement is active and strict
        if self.enforcement_level not in ["enforce", "strict"]:
            return None
        
        enforcement_active = self.cf.memory_query(f"session/{session_id}/enforcement_active") == "true"
        if not enforcement_active:
            return None
        
        # Get required tools
        required_tools_json = self.cf.memory_query(f"session/{session_id}/required_mcp_tools")
        if not required_tools_json:
            return None
        
        try:
            required_tools = json.loads(required_tools_json)
            if not required_tools:
                return None
        except json.JSONDecodeError:
            return None
        
        # Get used tools
        used_tools_json = self.cf.memory_query(f"session/{session_id}/mcp_tools_used")
        used_tools = json.loads(used_tools_json) if used_tools_json else []
        
        # Check if swarm_init is required but not used
        if "swarm_init" in required_tools and "swarm_init" not in used_tools:
            if current_tool in ["Task", "TodoWrite"] and not current_tool.startswith("mcp__"):
                return self._block_with_visual_guidance(
                    "REQUIRED MCP TOOL SKIPPED: swarm_init",
                    "MUST initialize swarm with mcp__claude-flow__swarm_init FIRST!",
                    "1. mcp__claude-flow__swarm_init 2. Then Task/TodoWrite",
                    "Skipping required MCP initialization"
                )
        
        # Check if other critical MCP tools are missing
        critical_tools = ["memory_usage", "task_orchestrate", "agent_spawn"]
        missing_critical = [t for t in critical_tools if t in required_tools and t not in used_tools]
        
        # Allow some operations before all tools are used, but warn
        if missing_critical and len(used_tools) < 2:
            # Get current message tools to check patterns
            message_key = f"session/{session_id}/current_message_tools"
            current_tools = json.loads(self.cf.memory_query(message_key) or "[]")
            
            # Count non-MCP tools
            non_mcp_count = sum(1 for t in current_tools if not t.startswith("mcp__"))
            
            if non_mcp_count > 3 and self.enforcement_level == "strict":
                missing_list = ", ".join([f"mcp__claude-flow__{t}" for t in missing_critical[:3]])
                return HookResponse(
                    decision=Decision.BLOCK.value,
                    reason=f"""
⚠️ MCP TOOLS ENFORCEMENT - USE REQUIRED TOOLS FIRST
═══════════════════════════════════════════════════

📋 Missing Required MCP Tools: {missing_list}

🔧 These tools were identified as MANDATORY for your task.
   Use them BEFORE proceeding with other operations!

💡 TIP: Start with MCP coordination tools, then do implementation.

⚡ ENFORCEMENT LEVEL: {self.enforcement_level.upper()}
"""
                )
        
        return None

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