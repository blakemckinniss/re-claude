# Claude Code Configuration with Python Hook System + ENFORCEMENT

## 🚨 CRITICAL: PARALLEL EXECUTION IS NOW ENFORCED!

**⚡ ENFORCEMENT ACTIVE**: The hook system now BLOCKS sequential operations and REQUIRES parallel execution:

### 🔴 MANDATORY CONCURRENT PATTERNS:

1. **TodoWrite**: ALWAYS batch ALL todos in ONE call (5-10+ todos minimum)
2. **Task tool**: ALWAYS spawn ALL agents in ONE message with full instructions
3. **File operations**: ALWAYS batch ALL reads/writes/edits in ONE message
4. **Bash commands**: ALWAYS batch ALL terminal operations in ONE message
5. **Memory operations**: ALWAYS batch ALL memory store/retrieve in ONE message

### ⚡ GOLDEN RULE: "1 MESSAGE = ALL RELATED OPERATIONS"

**Examples of CORRECT concurrent execution:**

```javascript
// ✅ CORRECT: Everything in ONE message
[Single Message]:
  - TodoWrite { todos: [10+ todos with all statuses/priorities] }
  - Task("Agent 1 with full instructions")
  - Task("Agent 2 with full instructions")
  - Task("Agent 3 with full instructions")
  - Read("file1.js")
  - Read("file2.js")
  - Write("output1.js", content)
  - Write("output2.js", content)
  - Bash("npm install")
  - Bash("npm test")
```

## 🔥 NEW: ENFORCEMENT SYSTEM

### Enforcement Levels (in settings.json)
- **suggest** 💡 - Gentle reminders about best practices
- **guide** 🎯 - Strong guidance with examples
- **enforce** ⚡ - Blocks violations (default)
- **strict** 🔥 - Maximum enforcement with auto-rewrite

### What Gets Enforced
1. **Sequential Operations BLOCKED** - No more "do X then Y"
2. **Batch Requirements** - TodoWrite must have 5-10+ items
3. **Parallel Task Spawning** - All agents in ONE message
4. **MCP-First for Complex Tasks** - Auto-injects requirements
5. **Required MCP Tools** - Must use specific tools from claude-flow's 87 tools

### MCP Tool Enforcement (87 Tools Available!)
The system now ENFORCES usage of claude-flow's 87 MCP tools based on task context:

#### How It Works:
1. **Pattern Detection** → Identifies task type (API, frontend, backend, etc.)
2. **Tool Mapping** → Selects REQUIRED tools from 87 available
3. **Early Blocking** → Prevents operations if required tools not used
4. **Validation Report** → Shows compliance at message completion

#### Tool Categories & Examples:
- **Swarm Orchestration** (9 tools): swarm_init, agent_spawn, task_orchestrate, topology_optimize
- **Neural/Cognitive** (9 tools): neural_train, pattern_recognize, cognitive_analyze, neural_predict
- **Memory Management** (9 tools): memory_usage, memory_search, memory_persist, memory_sync
- **Performance** (10 tools): bottleneck_analyze, performance_report, benchmark_run, metrics_collect
- **Workflow Automation** (9 tools): workflow_create, parallel_execute, scheduler_manage, batch_process
- **GitHub Integration** (6 tools): github_repo_analyze, github_pr_manage, github_code_review
- **Dynamic Agents** (6 tools): daa_agent_create, daa_capability_match, daa_consensus
- **System/Security** (8 tools): security_scan, backup_create, diagnostic_run, log_analysis

#### Example Enforcement:
```
🔧 MANDATORY MCP TOOLS (must use these):
  🕹️ mcp__claude-flow__workflow_create    [REQUIRED for API development]
  🕹️ mcp__claude-flow__bottleneck_analyze  [REQUIRED for performance tasks]
  🕹️ mcp__claude-flow__memory_usage       [REQUIRED for all tasks]
  🕹️ mcp__claude-flow__swarm_init         [REQUIRED for coordination]
  ... (+8 more required tools)
```

#### Early Blocking Example:
```
⚠️ MCP TOOLS ENFORCEMENT - USE REQUIRED TOOLS FIRST
═══════════════════════════════════════════════════

📋 Missing Required MCP Tools: mcp__claude-flow__swarm_init

🔧 These tools were identified as MANDATORY for your task.
   Use them BEFORE proceeding with other operations!

💡 TIP: Start with MCP coordination tools, then do implementation.
```

#### End-of-Message Validation:
```
🔍 MCP TOOL USAGE VALIDATION
═══════════════════════════════════════════════

📋 Required MCP Tools: 12
✅ Used MCP Tools: 8
❌ Missing Required Tools: 4

⚠️ MISSING REQUIRED TOOLS:
   ❌ mcp__claude-flow__workflow_create
   ❌ mcp__claude-flow__cognitive_analyze
   ❌ mcp__claude-flow__pattern_recognize
   ❌ mcp__claude-flow__memory_persist

📊 COMPLIANCE SCORE: 66.7%

💡 RECOMMENDATION: Review and use the missing required tools
These tools were identified as MANDATORY for your task complexity and patterns.
```

### Visual Violation Feedback
```
❌ CLAUDE-FLOW VIOLATION DETECTED
═══════════════════════════════════════

SEQUENTIAL TodoWrite DETECTED

✅ CORRECT PATTERN:
┌─ Single Message ─────────────────┐
│ • mcp__claude-flow__swarm_init   │
│ • Task (Agent 1-2-3) in parallel │
│ • TodoWrite (10+ todos)          │
│ • Read (multiple files)          │
└──────────────────────────────────┘

❌ YOUR PATTERN: Sequential operations

🔧 FIX: Batch ALL operations together!
```

## 🎯 Hook System Overview

This project uses a **Python-based hook system** that automatically enhances AND ENFORCES Claude Code patterns:

### Hook Types & Events

1. **UserPromptSubmit** - Analyzes your prompts before execution
   - Uses advanced prompt analyzer with optional Groq AI enhancement
   - Automatically suggests agent count and types
   - Provides task complexity analysis
   - Stores conversation context for better continuity

2. **PreToolUse** - Validates and prepares tool usage
   - Auto-spawns agents based on task complexity
   - Validates bash commands for safety
   - Blocks sensitive file modifications
   - Prepares memory context

3. **PostToolUse** - Handles post-execution tasks
   - Auto-formats Python files with `black`
   - Auto-formats JS/TS files with `prettier`
   - Tracks task completion
   - Updates memory state

4. **Stop/SubagentStop** - Session management
   - Saves session state
   - Generates summaries
   - Persists memory for next session

5. **Notification** - Inter-agent communication
   - Broadcasts important events
   - Shares memory updates

## 🧠 Automatic Task Analysis & Agent Spawning

The Python hook system automatically analyzes your tasks and spawns appropriate agents:

### Complexity Analysis
- **Low complexity (3-4 agents)**: Simple tasks, basic fixes, updates
- **Medium complexity (5-7 agents)**: Standard development tasks
- **High complexity (8-12 agents)**: Enterprise systems, distributed architectures

### Auto-Agent Selection
Based on keywords in your prompt, the system automatically spawns:
- **coordinator** - For non-trivial tasks requiring orchestration
- **researcher** - When research/analysis is needed
- **coder** - For implementation tasks
- **tester** - When testing/QA is mentioned
- **architect** - For design and architecture tasks
- **reviewer** - For code review and auditing
- **optimizer** - For performance improvements
- **documenter** - For documentation tasks

### Topology Selection
- **mesh** - Default for general tasks
- **hierarchical** - For tasks requiring coordination
- **ring** - For pipeline/sequential workflows
- **star** - For centralized hub architectures

## 💾 Memory & Persistence

The system includes built-in memory features:

### Local Memory Store
- Stored in `.claude/hooks/memory/memory-store.json`
- Persists across sessions
- Tracks decisions, context, and progress

### Claude Flow Memory Integration
When claude-flow is available:
```bash
# Store memory
npx claude-flow@alpha memory store <key> <value> --ttl 3600

# Query memory
npx claude-flow@alpha memory query <pattern>

# Session management
npx claude-flow@alpha memory store session_initialized "$(date -Iseconds)"
```

## 🎯 CRITICAL: Claude Code Does ALL Real Work

### ✅ Claude Code ALWAYS Handles:
- 🔧 **ALL file operations** (Read, Write, Edit, MultiEdit, Glob, Grep)
- 💻 **ALL code generation** and programming tasks
- 🖥️ **ALL bash commands** and system operations
- 🏗️ **ALL actual implementation** work
- 📝 **ALL TodoWrite** and task management
- 🔄 **ALL git operations**

### 🧠 MCP Tools ONLY Handle:
- 🎯 **Coordination only** - Planning Claude Code's actions
- 💾 **Memory management** - Storing decisions and context
- 🤖 **Swarm orchestration** - Coordinating multiple Claude Code instances

## 🔐 Security & Safety

### Allowed Commands (from settings.json)
- `npx claude-flow@alpha *`
- `npm run lint`, `npm test`
- `git` operations (status, diff, log, add, commit, push)
- `gh` (GitHub CLI)
- `node`, `python`
- Formatting tools: `black`, `prettier`
- Directory operations: `mkdir`, `ls`, `pwd`

### Blocked Patterns
- `rm -rf /`
- Remote code execution (`curl * | bash`)
- `sudo` commands
- Dangerous file operations

## 🚀 Auto-Formatting

Files are automatically formatted after editing:
- **Python files** (.py) - Formatted with `black`
- **JavaScript/TypeScript** (.js, .ts) - Formatted with `prettier`

This happens automatically via PostToolUse hooks - no manual action needed!

## 📋 MANDATORY TODO BATCHING

**TodoWrite Tool Requirements:**
1. **ALWAYS** include 5-10+ todos in a SINGLE TodoWrite call
2. **NEVER** call TodoWrite multiple times in sequence
3. **INCLUDE** all priority levels (high, medium, low) in one call

```javascript
// ✅ CORRECT - All todos in ONE call
TodoWrite { todos: [
  { id: "1", content: "Initialize system", status: "completed", priority: "high" },
  { id: "2", content: "Analyze requirements", status: "in_progress", priority: "high" },
  { id: "3", content: "Design architecture", status: "pending", priority: "high" },
  { id: "4", content: "Implement core", status: "pending", priority: "high" },
  { id: "5", content: "Build features", status: "pending", priority: "medium" },
  { id: "6", content: "Write tests", status: "pending", priority: "medium" },
  { id: "7", content: "Add monitoring", status: "pending", priority: "medium" },
  { id: "8", content: "Documentation", status: "pending", priority: "low" }
]}
```

## 🤖 Using MCP Tools for Coordination

When claude-flow MCP server is installed:

### Initialize Swarm
```javascript
mcp__claude-flow__swarm_init { 
  topology: "mesh",
  maxAgents: 6,
  strategy: "adaptive" 
}
```

### Spawn Agents
```javascript
mcp__claude-flow__agent_spawn { 
  type: "researcher",
  name: "API Research",
  capabilities: ["api", "documentation"]
}
```

### Memory Operations
```javascript
mcp__claude-flow__memory_usage {
  action: "store",
  key: "project/decision",
  value: "Use REST API pattern"
}
```

## 🎨 Prompt Enhancement

The UserPromptSubmit hook automatically enhances your prompts with:

1. **Task Analysis** - Complexity scoring and pattern detection
2. **Context Awareness** - Previous conversation history
3. **Agent Recommendations** - Optimal team composition
4. **MCP Tool Suggestions** - Relevant coordination tools
5. **Execution Instructions** - Step-by-step guidance
6. **Clear Action Items** - Specific next steps at the end

### Example Enhanced Output
```
📊 ENHANCED PROMPT ANALYSIS
════════════════════════════════════════
🎯 Task Type: Full-Stack Development
💡 Complexity: High (Score: 8/10)
🔧 Technologies: React, Node.js, PostgreSQL
📝 Analysis: Complex multi-tier application

👥 RECOMMENDED SWARM (8 agents)
• architect - System design
• coder (x2) - Frontend/Backend
• analyst - Database design
• tester - Quality assurance
• coordinator - Project management

🛠️ SUGGESTED MCP TOOLS
• swarm_init - Initialize coordination
• task_orchestrate - Manage workflow
• memory_usage - Track decisions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 NEXT ACTION (EXECUTE NOW):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Execute ALL of these in ONE message:
1️⃣ Initialize swarm with mcp__claude-flow__swarm_init (if complexity >= 4)
2️⃣ SPAWN 8 agents (architect, coder, analyst) using parallel Task calls
3️⃣ CREATE TodoWrite with 8-12 todos (mixed statuses/priorities)
4️⃣ READ any relevant files mentioned in the requirements
5️⃣ THEN: design the service architecture and data models

⚡ Remember: ALL operations above in ONE message for maximum efficiency!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Pattern-Specific First Actions
The system provides context-aware first actions based on detected patterns:

- **API Development**: "design the API structure and define endpoints"
- **Frontend Development**: "create the component architecture and UI flow"
- **Backend Development**: "design the service architecture and data models"
- **Database Operations**: "analyze the schema requirements and relationships"
- **Testing Automation**: "identify test scenarios and coverage requirements"
- **Performance Optimization**: "profile the current system and identify bottlenecks"
- **Security Audit**: "scan for vulnerabilities and review security patterns"
- **Debugging**: "reproduce the issue and gather diagnostic information"
- **Deployment**: "review the deployment requirements and infrastructure"
- **Refactoring**: "analyze the current code structure and identify improvements"
- **Documentation**: "outline the documentation structure and key topics"
- **Architecture Design**: "define system components and their interactions"

## 📊 Visual Progress Tracking

The system provides visual task tracking:

```
📊 Progress Overview
   ├── Total Tasks: 10
   ├── ✅ Completed: 3 (30%)
   ├── 🔄 In Progress: 2 (20%)
   ├── ⭕ Todo: 5 (50%)
   └── ❌ Blocked: 0 (0%)

🔄 In progress (2)
   ├── 🟡 002: Implement auth system ↳ 2 deps ▶
   └── 🔴 003: Design database schema [HIGH] ▶

Priority indicators: 🔴 HIGH/CRITICAL, 🟡 MEDIUM, 🟢 LOW
```

## 🔧 Configuration Files

### `.claude/settings.json`
- Hook configuration (PreToolUse, PostToolUse, etc.)
- Environment variables
- Security permissions
- MCP server settings
- **NEW**: `"claude_flow_enforcement": "enforce"` - Set enforcement level

### `.claude/hooks/`
- `claude_hook_router.py` - Main hook router with ENFORCEMENT
- `prompt_analyzer_main.py` - Prompt analysis with MCP injection
- `prompt_analyzer/` - Modular analysis components
- `memory/` - Local memory store with TTL support
- `memory/memory-store.json` - Persistent session data

## ⚡ Best Practices (NOW ENFORCED!)

1. **Batch Everything** - REQUIRED: Single messages for operations
2. **Let Hooks Work** - Enforcement happens automatically
3. **Trust Analysis** - Complexity triggers MCP requirements
4. **Use Memory** - Session tracking enforces patterns
5. **Parallel First** - Sequential patterns get BLOCKED

### Auto-Rewrite Example
If you say: "First do X, then do Y, and after that do Z"

The system rewrites to:
```
[🔄 REWRITTEN FOR PARALLEL EXECUTION]
Execute ALL operations concurrently:
• Initialize swarm with appropriate topology
• Spawn ALL required agents in parallel
• Create complete todo list (5-10+ items)
• Read ALL necessary files simultaneously
• Store decisions in memory for persistence
```

## 🚨 Important Notes

- **ENFORCEMENT IS ACTIVE** - Violations will be BLOCKED
- The Python hooks run automatically - no manual intervention needed
- Memory persists in `.claude/hooks/memory/memory-store.json`
- Auto-formatting requires `black` (Python) and `prettier` (JS/TS) installed
- Claude Flow integration enforced for complex tasks (score >= 4)
- All actual work is done by Claude Code - MCP tools coordinate
- Sequential patterns trigger auto-rewrite in enforce/strict modes

### Enforcement Violations Result In:
- ❌ **BLOCKED** operations with visual guidance
- 🔄 **AUTO-REWRITE** of sequential patterns
- 🚀 **FORCED MCP** initialization for complex tasks
- 📦 **BATCHING** requirements (5-10+ todos, parallel tasks)

---

Remember: **The hooks now ENFORCE claude-flow patterns automatically!**