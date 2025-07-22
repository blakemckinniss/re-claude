# Enhanced Prompt Analyzer for Claude Code

A modular, extensible prompt analysis system designed to enhance prompts for optimal Claude Code execution. This analyzer integrates deeply with claude-flow for intelligent task orchestration, agent recommendations, and MCP tool selection.

## Features

### 🧠 Advanced Task Analysis
- Pattern-based task recognition with 12+ predefined patterns
- Dynamic complexity scoring (1-10 scale)
- Technology stack detection
- Multi-pattern support for complex tasks

### 🐝 Intelligent Agent Recommendations
- Automatic agent count calculation based on complexity
- Role-based agent selection (coordinator, coder, tester, etc.)
- Hive mind coordination for enterprise-level tasks
- Dynamic scaling based on task requirements

### 🛠️ Smart MCP Tool Selection
- Context-aware tool recommendations
- Pattern-based tool mapping
- Complexity-driven tool selection
- Agent-specific tool suggestions

### 💡 Prompt Enhancement
- Structure analysis and improvement suggestions
- Missing component detection
- Clarity recommendations
- Approach suggestions based on complexity

### 🔄 Claude Flow Integration
- Memory persistence across sessions
- Conversation context tracking
- Performance bottleneck analysis
- Swarm orchestration commands

### 📊 Comprehensive Logging
- Structured JSON logging
- Automatic log rotation
- Performance metrics tracking
- Error context preservation

## Architecture

```
prompt_analyzer/
├── __init__.py              # Package initialization
├── core/                    # Core analyzer logic
│   ├── __init__.py
│   └── analyzer.py          # Main PromptAnalyzer class
├── models/                  # Data models
│   ├── __init__.py
│   ├── analysis.py          # AnalysisResult, TaskComplexity
│   ├── enhancement.py       # PromptEnhancement, ExecutionInstructions
│   └── patterns.py          # TaskPattern definitions
├── analyzers/               # Analysis components
│   ├── __init__.py
│   ├── task_analyzer.py     # Task pattern matching and complexity
│   ├── prompt_enhancer.py   # Prompt structure enhancement
│   └── context_manager.py   # Conversation context management
├── integrations/            # External service integrations
│   ├── __init__.py
│   ├── claude_flow.py       # Claude Flow command integration
│   └── groq_client.py       # Groq API client
└── utils/                   # Utility modules
    ├── __init__.py
    ├── logging.py           # Enhanced logging with rotation
    ├── formatting.py        # Output formatting
    └── config.py            # Configuration management
```

## Usage

### As a Claude Code Hook

```python
#!/usr/bin/env python3
from prompt_analyzer import PromptAnalyzer

# Initialize analyzer
analyzer = PromptAnalyzer()

# Analyze a prompt
output, analysis = analyzer.analyze(
    "Create a REST API with authentication",
    session_id="claude-20240122"
)

print(output)  # Formatted analysis for Claude Code
```

### Configuration

The analyzer can be configured via environment variables:

```bash
# Groq API Configuration
GROQ_API_KEY=your_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.3
GROQ_MAX_TOKENS=1024

# Claude Flow Configuration
CLAUDE_FLOW_TIMEOUT=30
MEMORY_NAMESPACE=claude-conversation
SESSION_TTL=86400

# Analysis Configuration
MAX_PROMPT_LENGTH=10240
MAX_PATTERNS=5
MAX_AGENTS=12
MAX_TOOLS=15

# Logging Configuration
LOG_DIR=/path/to/logs
LOG_LEVEL=INFO
MAX_LOG_SIZE_MB=10
MAX_LOG_FILES=5

# Feature Flags
USE_GROQ_SUMMARY=true
GROQ_SUMMARY_THRESHOLD=15
AUTO_SPAWN_AGENTS=true
ENABLE_HIVE_MIND=true
```

## Task Patterns

The analyzer recognizes these task patterns:

1. **API Development** - REST/GraphQL endpoint creation
2. **Frontend Development** - UI/component building
3. **Database Operations** - Schema design, migrations
4. **Testing Automation** - Unit/integration test creation
5. **Performance Optimization** - Speed and efficiency improvements
6. **Security Audit** - Vulnerability scanning and hardening
7. **Documentation** - README, guides, API docs
8. **Refactoring** - Code restructuring and modernization
9. **Deployment** - CI/CD pipeline setup
10. **Data Analysis** - Analytics and visualization
11. **Architecture Design** - System design and planning
12. **Debugging** - Bug fixing and troubleshooting

## Complexity Levels

| Level | Score | Agent Count | Description |
|-------|-------|-------------|-------------|
| TRIVIAL | 1 | 0 | Simple questions or queries |
| SIMPLE | 2 | 1 | Basic single-file changes |
| BASIC | 3 | 2 | Small feature additions |
| MODERATE | 4 | 3 | Standard development tasks |
| INTERMEDIATE | 5 | 4 | Multi-file features |
| COMPLEX | 6 | 5 | System-wide changes |
| ADVANCED | 7 | 6 | Architecture modifications |
| SOPHISTICATED | 8 | 8 | Enterprise features |
| ENTERPRISE | 9 | 10 | Large-scale systems |
| EXTREME | 10 | 12 | Mission-critical platforms |

## Output Format

The analyzer provides structured output including:

1. **Analysis Summary**
   - Topic classification
   - Complexity score and level
   - Detected technologies
   - Task patterns identified

2. **Enhancement Suggestions**
   - Structural improvements
   - Clarity recommendations
   - Missing components

3. **Swarm Orchestration**
   - Agent count and roles
   - MCP tool recommendations
   - Spawn commands

4. **Execution Instructions**
   - Step-by-step approach
   - Pattern-specific guidance
   - Critical reminders

## Integration with Claude Flow

The analyzer integrates with claude-flow for:

- **Memory Management**: Persistent context across sessions
- **Swarm Coordination**: Multi-agent task orchestration
- **Performance Analysis**: Bottleneck detection and optimization
- **Hive Mind**: Complex task consensus building

## Error Handling

The analyzer includes robust error handling:

- Graceful fallback when Groq is unavailable
- Local analysis as backup
- Comprehensive error logging
- Non-blocking operation (allows prompts to proceed)

## Performance

- Average analysis time: 50-200ms (local), 200-500ms (with Groq)
- Memory usage: ~50MB base + context
- Log rotation prevents disk space issues
- Caching reduces redundant API calls

## Contributing

When adding new features:

1. Add new task patterns to `models/patterns.py`
2. Update complexity calculations in `analyzers/task_analyzer.py`
3. Add new MCP tools to tool categories
4. Update agent role mappings
5. Add tests for new functionality

## License

This prompt analyzer is part of the Claude Flow ecosystem and follows the same licensing terms.