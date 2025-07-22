# Claude Flow @alpha Command Reference

A comprehensive guide to all available `npx claude-flow@alpha` commands and options.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Commands](#core-commands)
3. [Hive Mind Commands](#hive-mind-commands)
4. [Swarm Intelligence Commands](#swarm-intelligence-commands)
5. [Hook Commands](#hook-commands)
6. [Agent Management](#agent-management)
7. [Memory Operations](#memory-operations)
8. [GitHub Integration](#github-integration)
9. [SPARC Development](#sparc-development)
10. [Analysis & Performance](#analysis--performance)
11. [Coordination & Automation](#coordination--automation)
12. [Additional Commands](#additional-commands)

## Quick Start

```bash
# Install and initialize
npx claude-flow@alpha init --sparc

# Interactive hive mind setup (recommended)
npx claude-flow@alpha hive-mind wizard

# Start with UI and swarm
npx claude-flow@alpha start --ui --swarm

# Deploy multi-agent workflow
npx claude-flow@alpha swarm "Build REST API"
```

## Core Commands

### init - Initialize Claude Flow Environment

```bash
npx claude-flow@alpha init [options]
```

**Options:**
- `--force` - Overwrite existing configuration
- `--dry-run` - Preview what will be created
- `--basic` - Use basic initialization (pre-v2.0.0)
- `--sparc` - SPARC enterprise setup with additional features
- `--minimal` - Minimal setup without examples
- `--template <t>` - Use specific project template

**Creates:**
- `CLAUDE.md` - AI-readable project instructions & context
- `.claude/` - Enterprise configuration directory
- `.claude/commands/` - Custom commands and automation
- `.claude/settings.json` - Advanced configuration and hooks
- `.roomodes` - 17 specialized SPARC development modes

### start - Start Orchestration System

```bash
npx claude-flow@alpha start [options]
```

**Options:**
- `--ui` - Start with user interface
- `--swarm` - Enable swarm intelligence
- `--port <port>` - Specify port for UI
- `--background` - Run in background

### status - System Status

```bash
npx claude-flow@alpha status [options]
```

**Options:**
- `--verbose` - Detailed system information
- `--json` - JSON output format
- `--watch` - Live updates
- `--interval <ms>` - Update interval (with --watch)

## Hive Mind Commands

### hive-mind - Advanced Swarm Coordination

```bash
npx claude-flow@alpha hive-mind <subcommand> [options]
```

**Subcommands:**

#### wizard - Interactive Setup Wizard (Recommended)
```bash
npx claude-flow@alpha hive-mind wizard
```

#### init - Initialize Hive Mind System
```bash
npx claude-flow@alpha hive-mind init
```

#### spawn - Spawn Hive Mind Swarm
```bash
npx claude-flow@alpha hive-mind spawn [objective] [options]
```

**Options:**
- `--queen-type <type>` - Queen coordinator type (strategic, tactical, adaptive)
- `--max-workers <n>` - Maximum worker agents (default: 8)
- `--consensus <type>` - Consensus algorithm (majority, weighted, byzantine)
- `--memory-size <mb>` - Collective memory size in MB (default: 100)
- `--auto-scale` - Enable auto-scaling based on workload
- `--encryption` - Enable encrypted communication
- `--monitor` - Real-time monitoring dashboard
- `--verbose` - Detailed logging
- `--claude` - Generate Claude Code spawn commands with coordination
- `--auto-spawn` - Automatically spawn Claude Code instances
- `--execute` - Execute Claude Code spawn commands immediately

#### status - Show Hive Mind Status
```bash
npx claude-flow@alpha hive-mind status
```

#### sessions - List All Sessions
```bash
npx claude-flow@alpha hive-mind sessions
```

#### resume - Resume Paused Session
```bash
npx claude-flow@alpha hive-mind resume <session-id>
```

#### metrics - View Performance Metrics
```bash
npx claude-flow@alpha hive-mind metrics
```

## Swarm Intelligence Commands

### swarm - Multi-Agent AI Coordination

```bash
npx claude-flow@alpha swarm <objective> [options]
```

**Options:**
- `--strategy <type>` - Execution strategy: research, development, analysis, testing, optimization, maintenance
- `--mode <type>` - Coordination mode: centralized, distributed, hierarchical, mesh, hybrid
- `--max-agents <n>` - Maximum number of agents (default: 5)
- `--parallel` - Enable parallel execution (2.8-4.4x speed improvement)
- `--monitor` - Real-time swarm monitoring
- `--ui` - Interactive user interface
- `--background` - Run in background with progress tracking
- `--analysis` - Enable analysis/read-only mode (no code changes)
- `--read-only` - Enable read-only mode (alias for --analysis)

**Agent Types:**
- `researcher` - Research with web access and data analysis
- `coder` - Code development with neural patterns
- `analyst` - Performance analysis and optimization
- `architect` - System design with enterprise patterns
- `tester` - Comprehensive testing with automation
- `coordinator` - Multi-agent orchestration

### coordination - Swarm & Agent Orchestration

```bash
npx claude-flow@alpha coordination <command> [options]
```

**Commands:**

#### swarm-init - Initialize Swarm Infrastructure
```bash
npx claude-flow@alpha coordination swarm-init [options]
```

**Options:**
- `--swarm-id <id>` - Swarm identifier (auto-generated if not provided)
- `--topology <type>` - Coordination topology (hierarchical, mesh, ring, star, hybrid)
- `--max-agents <n>` - Maximum number of agents (default: 5)
- `--strategy <strategy>` - Coordination strategy (default: balanced)

#### agent-spawn - Spawn Coordinated Agents
```bash
npx claude-flow@alpha coordination agent-spawn [options]
```

**Options:**
- `--type <type>` - Agent type (coordinator, coder, developer, researcher, etc.)
- `--name <name>` - Custom agent name
- `--swarm-id <id>` - Target swarm for agent coordination
- `--capabilities <cap>` - Custom capabilities specification

#### task-orchestrate - Orchestrate Task Execution
```bash
npx claude-flow@alpha coordination task-orchestrate [options]
```

**Options:**
- `--task <description>` - Task description (required)
- `--swarm-id <id>` - Target swarm for task execution
- `--strategy <strategy>` - Coordination strategy (adaptive, parallel, sequential, hierarchical)
- `--share-results` - Enable result sharing across swarm

### automation - Intelligent Agent & Workflow Management

```bash
npx claude-flow@alpha automation <command> [options]
```

**Commands:**

#### auto-agent - Automatically Spawn Optimal Agents
```bash
npx claude-flow@alpha automation auto-agent [options]
```

**Options:**
- `--task-complexity <level>` - Task complexity (low, medium, high, enterprise)
- `--swarm-id <id>` - Target swarm ID for agent spawning

#### smart-spawn - Intelligently Spawn Agents
```bash
npx claude-flow@alpha automation smart-spawn [options]
```

**Options:**
- `--requirement <req>` - Specific requirement description
- `--max-agents <n>` - Maximum number of agents to spawn (default: 10)

#### workflow-select - Select Optimal Workflows
```bash
npx claude-flow@alpha automation workflow-select [options]
```

**Options:**
- `--project-type <type>` - Project type (web-app, api, data-analysis, enterprise, general)
- `--priority <priority>` - Optimization priority (speed, quality, cost, balanced)

## Hook Commands

### hooks - Lifecycle Event Management

```bash
npx claude-flow@alpha hooks <command> [options]
```

**Commands:**

#### pre-task - Execute Before Task Begins
```bash
npx claude-flow@alpha hooks pre-task [options]
```

**Options:**
- `--description <desc>` - Task description
- `--task-id <id>` - Task identifier
- `--agent-id <id>` - Executing agent identifier
- `--auto-spawn-agents` - Auto-spawn agents for task (default: true)

#### post-task - Execute After Task Completion
```bash
npx claude-flow@alpha hooks post-task [options]
```

**Options:**
- `--task-id <id>` - Task identifier
- `--analyze-performance` - Generate performance analysis
- `--generate-insights` - Create AI-powered insights

#### pre-edit - Execute Before File Modifications
```bash
npx claude-flow@alpha hooks pre-edit [options]
```

**Options:**
- `--file <path>` - Target file path
- `--operation <type>` - Edit operation type (edit, create, delete)

#### post-edit - Execute After File Modifications
```bash
npx claude-flow@alpha hooks post-edit [options]
```

**Options:**
- `--file <path>` - Modified file path
- `--memory-key <key>` - Coordination memory key for storing edit info

#### session-end - Execute at Session Termination
```bash
npx claude-flow@alpha hooks session-end [options]
```

**Options:**
- `--export-metrics` - Export session performance metrics
- `--swarm-id <id>` - Swarm identifier for coordination cleanup
- `--generate-summary` - Create comprehensive session summary

### Additional Hook Commands (from CLAUDE.md)

The following hooks are mentioned in CLAUDE.md but may not be fully documented:

#### notification - Store Decisions and Findings
```bash
npx claude-flow@alpha hooks notification --message "[what was done]" --telemetry true
```

#### session-restore - Restore Previous Session
```bash
npx claude-flow@alpha hooks session-restore --session-id "swarm-[id]" --load-memory true
```

#### pre-search - Check Coordination Before Search
```bash
npx claude-flow@alpha hooks pre-search --query "[what to check]" --cache-results true
```

## Agent Management

### agent - Manage Individual Agents

```bash
npx claude-flow@alpha agent <action> [options]
```

**Actions:**
- `spawn` - Create a new agent
- `list` - List all active agents
- `info` - Show agent details
- `terminate` - Stop an agent
- `hierarchy` - Manage agent hierarchies
- `ecosystem` - View agent ecosystem

**Options:**
- `--type <type>` - Agent type (coordinator, researcher, coder, analyst, architect, tester, reviewer, optimizer)
- `--name <name>` - Agent name
- `--verbose` - Detailed output
- `--json` - Output in JSON format

**Examples:**
```bash
npx claude-flow@alpha agent spawn researcher --name "Research Bot"
npx claude-flow@alpha agent list --json
npx claude-flow@alpha agent terminate agent-123
npx claude-flow@alpha agent info agent-456 --verbose
```

## Memory Operations

### memory - Manage Persistent Memory

```bash
npx claude-flow@alpha memory <action> [key] [value] [options]
```

**Actions:**
- `store` - Store data in memory
- `query` - Search memory by pattern
- `list` - List memory namespaces
- `export` - Export memory to file
- `import` - Import memory from file
- `clear` - Clear memory namespace

**Options:**
- `--namespace <name>` - Memory namespace (default: default)
- `--ttl <seconds>` - Time to live in seconds
- `--format <type>` - Export format (json, yaml)

**Examples:**
```bash
npx claude-flow@alpha memory store "api_design" "REST endpoints specification"
npx claude-flow@alpha memory query "authentication"
npx claude-flow@alpha memory export backup.json
npx claude-flow@alpha memory list --namespace project
```

## GitHub Integration

### github - Workflow Automation

```bash
npx claude-flow@alpha github <mode> <objective> [options]
```

**Modes:**
- `gh-coordinator` - GitHub workflow orchestration and CI/CD
- `pr-manager` - Pull request management with reviews
- `issue-tracker` - Issue management and project coordination
- `release-manager` - Release coordination and deployment
- `repo-architect` - Repository structure optimization
- `sync-coordinator` - Multi-package synchronization

**Options:**
- `--auto-approve` - Automatically approve safe changes
- `--dry-run` - Preview changes without applying
- `--verbose` - Detailed operation logging
- `--config <file>` - Custom configuration file

**Examples:**
```bash
npx claude-flow@alpha github pr-manager "create feature PR with tests"
npx claude-flow@alpha github gh-coordinator "setup CI/CD pipeline" --auto-approve
npx claude-flow@alpha github release-manager "prepare v2.0.0 release"
npx claude-flow@alpha github repo-architect "optimize monorepo structure"
```

## SPARC Development

### sparc - Execute SPARC Development Modes

```bash
npx claude-flow@alpha sparc <mode> [task] [options]
```

**Modes:**
- `spec` - Specification mode - Requirements analysis
- `architect` - Architecture mode - System design
- `tdd` - Test-driven development mode
- `integration` - Integration mode - Component connection
- `refactor` - Refactoring mode - Code improvement
- `modes` - List all available SPARC modes

**Options:**
- `--file <path>` - Input/output file path
- `--format <type>` - Output format (markdown, json, yaml)
- `--verbose` - Detailed output

**Examples:**
```bash
npx claude-flow@alpha sparc spec "User authentication system"
npx claude-flow@alpha sparc tdd "Payment processing module"
npx claude-flow@alpha sparc architect "Microservices architecture"
npx claude-flow@alpha sparc modes
```

## Analysis & Performance

### analysis - Performance & Usage Analytics

```bash
npx claude-flow@alpha analysis <command> [options]
```

**Commands:**

#### bottleneck-detect - Detect Performance Bottlenecks
```bash
npx claude-flow@alpha analysis bottleneck-detect [options]
```

**Options:**
- `--scope <scope>` - Analysis scope (system, swarm, agent, task, memory)
- `--target <target>` - Specific target to analyze (agent-id, swarm-id, task-type)

#### performance-report - Generate Performance Reports
```bash
npx claude-flow@alpha analysis performance-report [options]
```

**Options:**
- `--timeframe <time>` - Report timeframe (1h, 6h, 24h, 7d, 30d)
- `--format <format>` - Report format (summary, detailed, json, csv)

#### token-usage - Analyze Token Consumption
```bash
npx claude-flow@alpha analysis token-usage [options]
```

**Options:**
- `--agent <agent>` - Filter by agent type or ID
- `--breakdown` - Include detailed breakdown by agent type
- `--cost-analysis` - Include cost projections and optimization

### training - Neural Pattern Learning

```bash
npx claude-flow@alpha training <command> [options]
```

**Commands:**

#### neural-train - Train Neural Patterns
```bash
npx claude-flow@alpha training neural-train [options]
```

**Options:**
- `--data <source>` - Training data source (recent, historical, custom, swarm-<id>)
- `--model <name>` - Target model (general-predictor, task-predictor, agent-selector, performance-optimizer)
- `--epochs <n>` - Training epochs (default: 50)

#### pattern-learn - Learn From Operation Outcomes
```bash
npx claude-flow@alpha training pattern-learn [options]
```

**Options:**
- `--operation <op>` - Operation type to learn from
- `--outcome <result>` - Operation outcome (success/failure/partial)

#### model-update - Update Agent Models
```bash
npx claude-flow@alpha training model-update [options]
```

**Options:**
- `--agent-type <type>` - Agent type to update
- `--operation-result <res>` - Result from operation execution

## Additional Commands

### task - Manage Tasks and Workflows

```bash
npx claude-flow@alpha task <subcommand> [options]
```

**Examples:**
```bash
npx claude-flow@alpha task create research "Market analysis"
npx claude-flow@alpha task list --filter running
npx claude-flow@alpha task workflow examples/dev-flow.json
npx claude-flow@alpha task coordination status
```

### config - Manage System Configuration

```bash
npx claude-flow@alpha config <subcommand> [options]
```

**Examples:**
```bash
npx claude-flow@alpha config init
npx claude-flow@alpha config set terminal.poolSize 15
npx claude-flow@alpha config get orchestrator.maxConcurrentTasks
npx claude-flow@alpha config validate
```

### mcp - Manage MCP Server and Tools

```bash
npx claude-flow@alpha mcp <subcommand> [options]
```

**Examples:**
```bash
npx claude-flow@alpha mcp status
npx claude-flow@alpha mcp start --port 8080
npx claude-flow@alpha mcp tools --verbose
npx claude-flow@alpha mcp auth setup
```

### batch - Batch Operation Management

```bash
npx claude-flow@alpha batch <command> [options]
```

**Examples:**
```bash
npx claude-flow@alpha batch create-config my-batch.json
npx claude-flow@alpha batch create-config --interactive
npx claude-flow@alpha batch validate-config my-batch.json
npx claude-flow@alpha batch estimate my-batch.json
npx claude-flow@alpha batch list-templates
npx claude-flow@alpha batch list-environments
```

### migrate-hooks - Migrate Settings to Claude Code 1.0.51+

```bash
npx claude-flow@alpha migrate-hooks
```

Migrates settings.json to Claude Code 1.0.51+ format for compatibility.

## Key Features & Benefits

### Performance Improvements
- **84.8% SWE-Bench solve rate** - Better problem-solving through coordination
- **32.3% token reduction** - Efficient task breakdown reduces redundancy
- **2.8-4.4x speed improvement** - Parallel coordination strategies
- **27+ neural models** - Diverse cognitive approaches

### Enterprise Features
- 🐝 Queen-led hive mind coordination
- 🧠 Collective memory and knowledge sharing
- 🤝 Consensus building for critical decisions
- ⚡ Parallel task execution with auto-scaling
- 🔄 Work stealing and load balancing
- 📊 Real-time metrics and performance tracking
- 🛡️ Fault tolerance and self-healing
- 🔒 Secure communication between agents

### Integration Features
- Complete ruv-swarm integration with 87 MCP tools
- Neural network processing with WASM
- Multi-agent coordination topologies
- Cross-session memory persistence
- GitHub workflow automation
- Performance monitoring
- Enterprise security features

## Support & Resources

- **Documentation**: https://github.com/ruvnet/claude-flow
- **Issues**: https://github.com/ruvnet/claude-flow/issues
- **Examples**: https://github.com/ruvnet/claude-flow/tree/main/examples
- **Hive Mind Guide**: https://github.com/ruvnet/claude-flow/tree/main/docs/hive-mind
- **ruv-swarm**: https://github.com/ruvnet/ruv-FANN/tree/main/ruv-swarm

## Version Information

- **Current Version**: v2.0.0-alpha.68
- **Key Updates**: Complete ruv-swarm integration, neural networking, hive mind system
- **Alpha Features**: Fixed wrapper script to use @alpha tag, ensures latest version

---

**Remember**: Claude Flow coordinates, Claude Code creates! Start with `npx claude-flow@alpha hive-mind wizard` for the best experience.