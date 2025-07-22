# Claude Code Hooks Reference Guide

A comprehensive reference for implementing and using Claude Code Hooks for automation and workflow enhancement.

## Table of Contents

- [Overview](#overview)
- [Hook Events](#hook-events)
- [Configuration](#configuration)
- [Data Structures](#data-structures)
- [Communication Protocol](#communication-protocol)
- [Examples by Language](#examples-by-language)
- [Best Practices](#best-practices)
- [MCP Integration](#mcp-integration)
- [Security Considerations](#security-considerations)

## Overview

Claude Code hooks are user-defined shell commands that execute automatically at specific points in Claude Code's lifecycle. They provide deterministic, programmatic control over Claude Code's behavior, ensuring certain actions always happen rather than relying on the LLM to choose to run them.

### Key Benefits

- **Consistency**: Automated actions execute reliably every time
- **Speed**: Automate repetitive tasks and focus on creative work
- **Control**: Enforce project-specific rules and workflows
- **Integration**: Seamlessly connect with existing tools and scripts

## Hook Events

### 1. PreToolUse

**When**: Before Claude uses a specific tool  
**Can**: Block tool execution and provide feedback  
**Matcher**: Supports tool name patterns  

```json
{
  "decision": "approve" | "block" | undefined,
  "reason": "Explanation for decision"
}
```

### 2. PostToolUse

**When**: After a tool has been used successfully  
**Can**: Access tool output via `$CLAUDE_TOOL_OUTPUT`  
**Matcher**: Supports tool name patterns  

### 3. UserPromptSubmit

**When**: When user submits a prompt, before Claude processes it  
**Can**: Block prompts, add context, validate input  
**Matcher**: Not applicable  

### 4. Notification

**When**: When Claude sends a notification  
**Can**: Customize notification handling  
**Matcher**: Not applicable  

### 5. Stop

**When**: When main Claude Code agent finishes responding  
**Can**: Block Claude from stopping  
**Matcher**: Not applicable  

### 6. SubagentStop

**When**: When a Claude Code subagent (Task tool) finishes  
**Can**: Control subagent completion  
**Matcher**: Not applicable  

## Configuration

### JSON Format (`.claude/settings.json`)

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "your-command-here",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### TOML Format (`.claude/settings.toml`)

```toml
[[hooks]]
event = "PostToolUse"
run_in_background = false

[hooks.matcher]
tool_name = "Edit|MultiEdit|Write"
file_paths = ["*.py", "*.js"]

command = "echo 'File modified: $CLAUDE_FILE_PATHS'"
```

### Interactive Configuration

Use `/hooks` command in Claude Code for a menu-driven configuration interface.

## Data Structures

### Hook Input (via stdin)

All hooks receive JSON data via stdin:

```json
{
  "session_id": "uuid",
  "transcript_path": "/path/to/transcript.jsonl",
  "hook_event_name": "EventName",
  "tool_name": "ToolName",
  "tool_input": {
    "file_path": "/path/to/file",
    "command": "command string",
    // ... other tool-specific parameters
  },
  "tool_output": "output string (PostToolUse only)"
}
```

### Control Response Structure

```json
{
  "decision": "approve" | "block",
  "reason": "Explanation string",
  "continue": true | false,
  "stopReason": "Message when continue is false",
  "suppressOutput": true | false
}
```

## Communication Protocol

### Exit Codes

- **0**: Success
- **1**: General error
- **2**: Block action (PreToolUse hooks)

### Output Handling

- **stdout**: Shown to user in transcript mode (Ctrl-R)
- **stderr**: Fed back to Claude automatically
- **JSON output**: Parsed for control decisions

### Environment Variables

- `$CLAUDE_TOOL_OUTPUT`: Tool execution output (PostToolUse only)
- `$CLAUDE_FILE_PATHS`: Modified file paths
- `$CLAUDE_NOTIFICATION`: Notification content

## Examples by Language

### Python Example: Security Validator

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

import json
import sys
import re

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    
    # Block modifications to sensitive files
    sensitive_patterns = [".env", "secrets.json", ".git/"]
    
    for pattern in sensitive_patterns:
        if pattern in file_path:
            output = {
                "decision": "block",
                "reason": f"Cannot modify sensitive file: {file_path}"
            }
            print(json.dumps(output))
            sys.exit(0)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### JavaScript/Node.js Example: Code Formatter

```javascript
#!/usr/bin/env node

const fs = require('fs');
const { execSync } = require('child_process');

// Read input from stdin
let inputData = '';
process.stdin.on('data', chunk => inputData += chunk);
process.stdin.on('end', () => {
    try {
        const data = JSON.parse(inputData);
        const filePath = data.tool_input?.file_path;
        
        if (filePath?.endsWith('.js') || filePath?.endsWith('.ts')) {
            execSync(`npx prettier --write "${filePath}"`, { stdio: 'inherit' });
            console.error(`Formatted: ${filePath}`);
        }
        
        process.exit(0);
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
});
```

### Bash Example: Auto-commit

```bash
#!/bin/bash
# Auto-commit after file modifications

# Parse JSON input
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -n "$FILE_PATH" ]; then
    # Check if file is in a git repo
    if git -C "$(dirname "$FILE_PATH")" rev-parse --git-dir > /dev/null 2>&1; then
        cd "$(dirname "$FILE_PATH")"
        git add "$FILE_PATH"
        git commit -m "Auto-commit: Modified $(basename "$FILE_PATH")" > /dev/null 2>&1
        echo "Auto-committed changes to $FILE_PATH" >&2
    fi
fi

exit 0
```

## Best Practices

### 1. Auto-formatting Hook

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|MultiEdit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'FILE=$(echo \"$1\" | jq -r .tool_input.file_path); case \"$FILE\" in *.py) black \"$FILE\" ;; *.js|*.ts) npx prettier --write \"$FILE\" ;; *.go) gofmt -w \"$FILE\" ;; esac' -- "
          }
        ]
      }
    ]
  }
}
```

### 2. Test Runner Hook

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "run_in_background": true,
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | grep -E '\\.(py|js|ts)$' && npm test"
          }
        ]
      }
    ]
  }
}
```

### 3. Logging Hook

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '\"[\" + .session_id[0:8] + \"] \" + .tool_name + \": \" + (.tool_input.command // \"no command\")' >> ~/.claude/command-log.txt"
          }
        ]
      }
    ]
  }
}
```

### 4. Prompt Enhancement Hook

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/enhance-prompt.py"
          }
        ]
      }
    ]
  }
}
```

## MCP Integration

Hooks work seamlessly with Model Context Protocol (MCP) tools. MCP tools follow the pattern `mcp__<server>__<tool>`.

### Example: Memory Operation Logger

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__memory__*",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"Memory operation: $(date)\" | jq -Rs . >> ~/mcp-memory-log.json"
          }
        ]
      }
    ]
  }
}
```

## Security Considerations

### 1. Input Validation

Always validate and sanitize inputs:

```bash
# Good: Quoted variables
FILE_PATH="$1"

# Bad: Unquoted variables
FILE_PATH=$1
```

### 2. Path Traversal Protection

```python
import os

def is_safe_path(path):
    # Resolve to absolute path
    abs_path = os.path.abspath(path)
    # Check if it's within project directory
    project_root = os.path.abspath(".")
    return abs_path.startswith(project_root) and ".." not in path
```

### 3. Command Injection Prevention

```bash
# Use arrays for commands
CMD=("git" "commit" "-m" "$MESSAGE")
"${CMD[@]}"

# Avoid string concatenation
# BAD: eval "git commit -m '$MESSAGE'"
```

### 4. Timeout Configuration

Set appropriate timeouts to prevent hanging:

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "long-running-script.sh",
      "timeout": 30
    }
  ]
}
```

## Troubleshooting

### Debug Mode

Enable verbose logging:

```bash
export CLAUDE_DEBUG=1
```

### Test Hooks Manually

```bash
# Test a hook with sample input
echo '{"tool_name":"Edit","tool_input":{"file_path":"test.py"}}' | ./my-hook.sh
```

### Common Issues

1. **Hook not firing**: Check matcher patterns and event names
2. **Permission denied**: Ensure hook scripts are executable (`chmod +x`)
3. **JSON parsing errors**: Validate JSON output format
4. **Timeouts**: Adjust timeout values for long-running operations

## Advanced Patterns

### Conditional Execution

```bash
#!/bin/bash
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')

case "$TOOL_NAME" in
  "Write")
    # Handle file creation
    ;;
  "Edit"|"MultiEdit")
    # Handle file modification
    ;;
  *)
    # Default case
    ;;
esac
```

### Chain Multiple Actions

```python
#!/usr/bin/env python3
import json
import sys
import subprocess

def run_pipeline(file_path):
    steps = [
        ["black", file_path],
        ["flake8", file_path],
        ["mypy", file_path]
    ]
    
    for step in steps:
        try:
            subprocess.run(step, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Pipeline failed at: {' '.join(step)}", file=sys.stderr)
            return False
    
    return True
```

### Dynamic Hook Loading

```javascript
const hooks = require('~/.claude/hooks/registry.json');
const eventHooks = hooks[process.env.HOOK_EVENT_NAME] || [];

eventHooks.forEach(hook => {
    if (matchesPattern(input, hook.pattern)) {
        executeHook(hook);
    }
});
```

## Performance Tips

1. **Use `run_in_background`** for non-blocking operations
2. **Cache expensive computations** between hook invocations
3. **Batch operations** when possible
4. **Use appropriate timeouts** to prevent blocking
5. **Log to files asynchronously** to avoid I/O blocking

## Resources

- [Official Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [Hooks Guide](https://docs.anthropic.com/en/docs/claude-code/hooks-guide)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Community Examples](https://github.com/disler/claude-code-hooks-mastery)

---

This reference guide provides comprehensive information for implementing Claude Code hooks. For the latest updates and additional examples, refer to the official Anthropic documentation.