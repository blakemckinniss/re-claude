# Claude Hook Router Improvements for claude-flow Alignment

## 1. Replace Subprocess with Direct MCP Calls

Instead of:
```python
def memory_store(key: str, value: str, ttl: Optional[int] = None) -> bool:
    cmd = ["npx", "claude-flow@alpha", "memory", "store", key, value]
    # subprocess approach
```

Should be:
```python
def memory_store(key: str, value: str, ttl: Optional[int] = None) -> bool:
    # Direct MCP tool invocation
    return mcp__claude_flow__memory_usage({
        "action": "store",
        "key": key,
        "value": value,
        "ttl": ttl
    })
```

## 2. Enforce Parallel Execution Patterns

Add validation in pre-tool handlers:
```python
def _handle_pre_todo_write(self, hook_input: HookInput) -> HookResponse:
    todos = hook_input.tool_input.get("todos", [])
    
    # Enforce minimum batch size
    if len(todos) < 5:
        return HookResponse(
            decision=Decision.BLOCK.value,
            reason="TodoWrite must include at least 5-10 todos in a single call. Batch all todos together!"
        )
    
    # Check for proper status distribution
    statuses = [todo.get("status") for todo in todos]
    if all(s == "pending" for s in statuses):
        return HookResponse(
            decision=Decision.BLOCK.value,
            reason="Include mixed statuses (completed, in_progress, pending) to show progress"
        )
```

## 3. Auto-Inject MCP Coordination

In UserPromptSubmit handler:
```python
def _handle_user_prompt_submit(self, hook_input: HookInput) -> HookResponse:
    prompt = hook_input.tool_input.get("prompt", "")
    
    # Auto-inject swarm command for complex tasks
    complexity, agent_count = self.analyzer.analyze_complexity(prompt)
    
    if complexity in ["medium", "high"]:
        enhanced_prompt = f"""
{prompt}

[AUTO-INJECTED COORDINATION]
1. Initialize swarm: mcp__claude-flow__swarm_init
2. Spawn {agent_count} agents in parallel
3. Use mcp__claude-flow__memory_usage to track decisions
4. Execute ALL operations concurrently
"""
        hook_input.tool_input["prompt"] = enhanced_prompt
```

## 4. Enforce MCP-First Patterns

Add pre-execution checks:
```python
def _handle_pre_task(self, hook_input: HookInput) -> HookResponse:
    # Check if MCP swarm is initialized for complex tasks
    if not self._is_swarm_initialized() and self._is_complex_task(hook_input):
        return HookResponse(
            decision=Decision.BLOCK.value,
            reason="Complex task detected! Initialize swarm first with mcp__claude-flow__swarm_init"
        )
```

## 5. Add Visual Progress Tracking

Enhance post-tool handlers:
```python
def _handle_post_todo_write(self, hook_input: HookInput) -> HookResponse:
    todos = hook_input.tool_input.get("todos", [])
    
    # Generate visual progress
    completed = sum(1 for t in todos if t["status"] == "completed")
    in_progress = sum(1 for t in todos if t["status"] == "in_progress")
    pending = sum(1 for t in todos if t["status"] == "pending")
    
    progress_visual = f"""
📊 Task Progress Update:
   ├── ✅ Completed: {completed} ({completed/len(todos)*100:.0f}%)
   ├── 🔄 In Progress: {in_progress} ({in_progress/len(todos)*100:.0f}%)
   └── ⭕ Pending: {pending} ({pending/len(todos)*100:.0f}%)
"""
    self._log_info(progress_visual)
```

## 6. Strengthen Memory Patterns

Auto-store important context:
```python
def _handle_post_file_operation(self, hook_input: HookInput) -> HookResponse:
    file_path = hook_input.tool_input.get("file_path", "")
    
    # Auto-store file operations in memory
    self.cf.memory_store(
        f"session/{self.session_id}/files_modified",
        json.dumps({
            "file": file_path,
            "operation": hook_input.tool_name,
            "timestamp": time.time()
        })
    )
```

## 7. Add Coordination Reminders

In all response messages:
```python
def _generate_coordination_reminder(self, context: str) -> str:
    return f"""
🤖 COORDINATION REMINDER:
• Use mcp__claude-flow__swarm_init for complex tasks
• Spawn agents with mcp__claude-flow__agent_spawn
• Store decisions with mcp__claude-flow__memory_usage
• Execute operations in PARALLEL (single message)
"""
```

These improvements would make the hook router more actively enforce claude-flow patterns and guide users toward proper MCP tool usage.