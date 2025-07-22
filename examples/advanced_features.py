#!/usr/bin/env python3
"""
Advanced features demonstration of the modular prompt analyzer
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt_analyzer import PromptAnalyzer
from prompt_analyzer.models import TaskComplexity, AnalysisResult
from prompt_analyzer.analyzers import TaskAnalyzer, PromptEnhancer
from prompt_analyzer.utils import Config, Logger
from prompt_analyzer.models.patterns import TASK_PATTERNS

# Example 1: Custom Configuration
print("=" * 60)
print("Example 1: Custom Configuration")
print("=" * 60)

# Create custom config
custom_config = Config(
    max_agents=15,
    max_tools=20,
    groq_temperature=0.5,
    enable_hive_mind=True,
    log_level="DEBUG"
)

analyzer = PromptAnalyzer(custom_config)
print(f"Custom config created with max_agents={custom_config.max_agents}")

# Example 2: Direct Component Usage
print("\n" + "=" * 60)
print("Example 2: Using Components Directly")
print("=" * 60)

# Use task analyzer directly
task_analyzer = TaskAnalyzer()
prompt = "Build a real-time chat application with WebSocket support"

# Get detailed task analysis
task_result = task_analyzer.analyze_prompt(prompt)
print(f"Prompt: {prompt}")
print(f"Patterns detected: {[p.name for p in task_result['patterns']]}")
print(f"Complexity: {task_result['complexity'].name} (score: {task_result['complexity_score']})")
print(f"Technologies: {task_result['tech_involved']}")

# Example 3: Prompt Enhancement
print("\n" + "=" * 60)
print("Example 3: Prompt Enhancement Details")
print("=" * 60)

enhancer = PromptEnhancer()
vague_prompt = "make website"

# Analyze structure
structure = enhancer.analyze_prompt_structure(vague_prompt)
print(f"Vague prompt: '{vague_prompt}'")
print(f"Structure analysis: {json.dumps(structure, indent=2)}")

# Get enhancement suggestions
enhancement = enhancer.enhance_prompt(
    vague_prompt,
    {"complexity_score": 3},
    []
)

print(f"\nEnhancement suggestions:")
for clarification in enhancement.clarifications:
    print(f"  • {clarification}")

# Example 4: Pattern Exploration
print("\n" + "=" * 60)
print("Example 4: Available Task Patterns")
print("=" * 60)

print("All recognized patterns:")
for i, pattern in enumerate(TASK_PATTERNS, 1):
    print(f"{i:2d}. {pattern.name.replace('_', ' ').title()}")
    print(f"    Keywords: {', '.join(pattern.keywords[:5])}")
    print(f"    Complexity modifier: {pattern.complexity_modifier:+d}")
    print(f"    Required agents: {', '.join(pattern.required_agents)}")
    print()

# Example 5: Logging and Debugging
print("\n" + "=" * 60)
print("Example 5: Logging and Debugging")
print("=" * 60)

# Create logger
logger = Logger("example_app")

# Log analysis event
logger.log_analysis(
    prompt="Create a REST API",
    analysis={
        "complexity_score": 5,
        "topic_genre": "API Development",
        "swarm_agents_recommended": 4
    },
    duration_ms=150
)

print("Analysis logged to ~/.claude/logs/example_app.log")

# Example 6: Working with Analysis Results
print("\n" + "=" * 60)
print("Example 6: Working with Analysis Results")
print("=" * 60)

# Create an AnalysisResult object
result = AnalysisResult(
    topic_genre="Web Development",
    complexity_score=6,
    complexity_level=TaskComplexity.COMPLEX,
    tech_involved=["React", "Node.js", "PostgreSQL"],
    analysis_notes="Full-stack web application with database",
    swarm_agents_recommended=5,
    recommended_agent_roles=["coordinator", "frontend-dev", "backend-dev", "database-specialist", "tester"],
    recommended_mcp_tools=["swarm_init", "agent_spawn", "workflow_create", "parallel_execute"],
    task_patterns=["frontend_development", "api_development", "database_operations"],
    confidence_score=0.85
)

print(f"Analysis Result Summary:")
print(f"  Topic: {result.topic_genre}")
print(f"  Complexity: {result.complexity_level.name} ({result.complexity_score}/10)")
print(f"  Confidence: {result.confidence_score:.1%}")
print(f"  Agent Count: {result.swarm_agents_recommended}")

# Convert to dict for JSON serialization
result_dict = result.to_dict()
print(f"\nJSON representation: {json.dumps(result_dict, indent=2)}")

# Example 7: Error Handling
print("\n" + "=" * 60)
print("Example 7: Error Handling")
print("=" * 60)

# Test with invalid prompt
try:
    output, analysis = analyzer.analyze("")  # Empty prompt
except Exception as e:
    print(f"Error handled gracefully: {e}")

# The analyzer actually returns empty output for too-short prompts
output, analysis = analyzer.analyze("Hi")
if analysis.get("error"):
    print(f"Short prompt handled: {analysis['error']}")
else:
    print("Short prompt processed successfully")