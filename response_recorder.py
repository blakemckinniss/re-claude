#!/usr/bin/env python3
"""
Claude Code Response Recorder - Captures Claude's outputs from transcript

This script is called by the Stop hook to record Claude's responses,
maintaining full conversation history to prevent context poisoning.
"""

import json
import sys
import os
import time
from datetime import datetime

def read_transcript(transcript_path):
    """Read the transcript JSONL file and extract the last assistant response"""
    if not os.path.exists(transcript_path):
        return None, None
    
    # Read the transcript (JSONL format - one JSON object per line)
    events = []
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
    except Exception as e:
        return None, None
    
    # Find the last user prompt and assistant response
    last_prompt = None
    last_response = None
    response_parts = []
    collecting_response = False
    
    for event in events:
        event_type = event.get('type', '')
        
        # Track user prompts
        if event_type == 'userPrompt':
            last_prompt = event.get('prompt', '')
            collecting_response = True
            response_parts = []
        
        # Collect assistant messages after the last prompt
        elif event_type == 'assistantMessage' and collecting_response:
            content = event.get('message', '')
            if content:
                response_parts.append(content)
        
        # Stop collecting when we hit the next user prompt
        elif event_type == 'userPrompt' and response_parts:
            last_response = '\n'.join(response_parts)
            response_parts = []
    
    # If we were still collecting at the end, that's our response
    if response_parts:
        last_response = '\n'.join(response_parts)
    
    return last_prompt, last_response

def extract_key_actions(response):
    """Extract key actions from Claude's response"""
    if not response:
        return []
    
    actions = []
    
    # Look for tool usage patterns
    tool_patterns = [
        ('TodoWrite', 'task management'),
        ('Edit', 'file editing'),
        ('Write', 'file creation'),
        ('Read', 'file reading'),
        ('Bash', 'command execution'),
        ('Task', 'agent spawning'),
        ('mcp__', 'MCP tool usage'),
        ('WebSearch', 'web search'),
        ('WebFetch', 'web content fetch'),
        ('Glob', 'file search'),
        ('Grep', 'content search')
    ]
    
    for pattern, action_type in tool_patterns:
        if pattern in response:
            actions.append(action_type)
    
    # Look for code blocks (indicates code generation)
    if '```' in response:
        actions.append('code generation')
    
    return list(set(actions))  # Remove duplicates

def summarize_response(response, max_length=500):
    """Create a concise summary of Claude's response"""
    if not response:
        return "No response captured"
    
    # Remove code blocks and tool calls for summary
    lines = response.split('\n')
    summary_lines = []
    in_code_block = False
    in_tool_call = False
    
    for line in lines:
        # Toggle code block state
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        # Check for tool call markers
        if '<function_calls>' in line or '<function_calls>' in line:
            in_tool_call = True
            continue
        elif '</function_calls>' in line or '