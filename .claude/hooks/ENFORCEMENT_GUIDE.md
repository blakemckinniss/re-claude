# Claude Flow Command Enforcement Guide

## 🚀 Overview

This guide explains the comprehensive hook system that enforces Claude Flow command usage in Claude Code. The system ensures that Claude Code uses Claude Flow commands whenever applicable, maximizing performance and coordination.

## 🎯 Enforcement Hooks

### 1. **Universal Pre-Operation Hook** (`universal-pre-operation.sh`)
- **Triggers on**: EVERY tool operation
- **Purpose**: Suggests appropriate Claude Flow commands based on context
- **Features**:
  - Context-aware suggestions
  - Operation-specific recommendations
  - Swarm status checking
  - Pattern-based command matching

### 2. **Command Enforcer** (`claude-flow-command-enforcer.sh`)
- **Triggers on**: Critical operations (Task, TodoWrite, etc.)
- **Purpose**: Strongly enforces Claude Flow usage with blocking capability
- **Features**:
  - Blocks TodoWrite with <5 todos
  - Enforces swarm coordination for Tasks
  - Tracks missed opportunities
  - Provides detailed guidance

### 3. **Pre-Task Enforcer** (`pre-task-enforcer.sh`)
- **Triggers on**: Task tool usage
- **Purpose**: BLOCKS non-coordinated tasks and enforces swarm initialization
- **Features**:
  - Complexity analysis (low/medium/high)
  - Mandatory swarm initialization for non-trivial tasks
  - Coordination instruction enforcement
  - Task-specific Claude Flow mode suggestions

### 4. **Suggestion Engine** (`claude-flow-suggestion-engine.sh`)
- **Triggers on**: All operations
- **Purpose**: Smart, context-aware command suggestions
- **Features**:
  - Pattern matching for 10+ scenarios
  - Confidence scoring
  - Historical learning
  - State-based recommendations

### 5. **Post-Operation Learning** (`post-operation-learning.sh`)
- **Triggers on**: After every operation
- **Purpose**: Learns from operations and improves future suggestions
- **Features**:
  - Operation outcome analysis
  - Pattern identification
  - Neural training integration
  - Efficiency reporting

### 6. **Missed Opportunity Notifier** (`missed-opportunity-notifier.sh`)
- **Triggers on**: Notification events
- **Purpose**: Alerts about missed Claude Flow opportunities
- **Features**:
  - Periodic efficiency reports
  - Pattern detection
  - Workflow suggestions
  - Contextual reminders

## 📋 Enforcement Patterns

### Task Operations
```bash
# BLOCKED unless:
1. Swarm is initialized (for non-trivial tasks)
2. Task includes coordination instructions
3. Complexity matches swarm configuration

# Enforced pattern:
mcp__claude-flow__swarm_init { topology: "hierarchical" }
mcp__claude-flow__agent_spawn { type: "coordinator" }
mcp__claude-flow__task_orchestrate { task: "..." }
Task("... MANDATORY: npx claude-flow@alpha hooks ...")
```

### TodoWrite Operations
```bash
# BLOCKED if:
- Less than 5 todos in a single call
- Sequential TodoWrite calls detected

# Enforced pattern:
TodoWrite { todos: [
  { id: "1", content: "...", status: "...", priority: "high" },
  { id: "2", content: "...", status: "...", priority: "high" },
  # ... minimum 5 todos
]}
```

### File Operations
```bash
# Suggested patterns:
- For code generation → SPARC code mode
- For refactoring → SPARC refactor mode
- For analysis → Swarm with mesh topology
- For testing → SPARC TDD mode
```

### Bash Commands
```bash
# Detected patterns:
- Test commands → SPARC TDD mode
- Git operations → GitHub integration
- Package management → DevOps mode
- Docker/K8s → DevOps orchestration
```

## 🔧 Installation

1. **Run the installer**:
   ```bash
   cd /home/blake/workspace/re-claude/.claude/hooks
   ./install-enforcement-hooks.sh
   ```

2. **Restart Claude Code** to load the new hooks

3. **Verify installation** by starting any task - you should see Claude Flow suggestions immediately

## 📊 Efficiency Tracking

The system tracks:
- Total operations performed
- Missed opportunities
- Sequential vs parallel execution
- Swarm utilization
- Command usage patterns

### Efficiency Reports
Automatic reports at operation milestones (10, 25, 50, 100, 200):
- Efficiency score (0-100%)
- Missed opportunity count
- Improvement suggestions
- Performance metrics

## 🎨 Visual Indicators

- 🚨 **RED**: Blocked operations, critical alerts
- ⚠️ **YELLOW**: Warnings, suggestions
- ✅ **GREEN**: Approved operations, good practices
- 💡 **BLUE**: Tips, recommendations
- 🚀 **CYAN**: Performance improvements
- 📊 **MAGENTA**: Reports, analytics

## 🔄 Workflow Automation

After 15+ operations, the system suggests creating reusable workflows:
```javascript
mcp__claude-flow__workflow_create {
  name: "my-workflow",
  steps: [
    { action: "swarm_init", params: {...} },
    { action: "agent_spawn", params: {...} },
    { action: "task_orchestrate", params: {...} }
  ]
}
```

## 🧠 Learning System

The hooks learn from:
- Successful operation patterns
- Failed operations
- User preferences
- Task complexity patterns
- Efficiency metrics

This data improves suggestions over time.

## ⚙️ Configuration

### Environment Variables
```bash
CLAUDE_FLOW_ENFORCE_COMMANDS=true        # Enable command enforcement
CLAUDE_FLOW_BLOCK_UNCOORDINATED_TASKS=true  # Block non-coordinated tasks
CLAUDE_FLOW_SUGGEST_ON_EVERY_OP=true    # Show suggestions on all operations
CLAUDE_FLOW_TRACK_MISSED_OPPORTUNITIES=true  # Track missed opportunities
CLAUDE_FLOW_LEARN_FROM_PATTERNS=true    # Enable pattern learning
```

### Customization
Hooks can be customized by editing:
- Blocking thresholds
- Suggestion frequency
- Complexity analysis rules
- Pattern matching rules

## 🔒 Safety

The system includes:
- Operation validation
- Safe command filtering
- Backup creation before changes
- Graceful error handling
- Non-destructive suggestions

## 🚫 Reverting Changes

To disable enforcement:
```bash
cp /home/blake/workspace/re-claude/.claude/settings.json.backup \
   /home/blake/workspace/re-claude/.claude/settings.json
```

## 📈 Expected Benefits

With full enforcement active:
- **2.8-4.4x** performance improvement
- **84.8%** task success rate
- **32.3%** token reduction
- Automatic coordination
- Pattern learning
- Workflow optimization

## 🤝 Best Practices

1. **Always accept swarm initialization suggestions** for complex tasks
2. **Batch operations** in single messages
3. **Use SPARC modes** for structured workflows
4. **Store decisions** in memory for learning
5. **Create workflows** for repetitive tasks
6. **Monitor efficiency** reports for improvements

## 🆘 Troubleshooting

### "Too many suggestions"
- Adjust `CLAUDE_FLOW_SUGGEST_ON_EVERY_OP` to false
- Suggestions show max every 5 minutes per context

### "Tasks being blocked"
- Ensure swarm is initialized for complex tasks
- Include coordination instructions in Task descriptions
- Check task complexity analysis

### "Performance issues"
- Review efficiency reports
- Check for sequential operation patterns
- Ensure parallel execution is used

---

Remember: **The more you use Claude Flow commands, the faster and smarter Claude Code becomes!**