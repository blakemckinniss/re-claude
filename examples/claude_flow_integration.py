#!/usr/bin/env python3
"""
Example demonstrating claude-flow integration features
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt_analyzer.integrations import ClaudeFlowIntegration
from prompt_analyzer.analyzers import ConversationContextManager
from prompt_analyzer import PromptAnalyzer

# Example 1: Direct Claude Flow Integration
print("=" * 60)
print("Example 1: Direct Claude Flow Commands")
print("=" * 60)

cf = ClaudeFlowIntegration()

# Store a value in memory
key = "project_context"
value = json.dumps({
    "project": "E-commerce API",
    "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
    "status": "in_progress"
})

success = cf.memory_store(key, value, namespace="demo-project")
print(f"Stored project context: {success}")

# Query memory
entries = cf.memory_query("project_*", namespace="demo-project")
print(f"Found {len(entries)} memory entries")

# Example 2: Session Management
print("\n" + "=" * 60)
print("Example 2: Session and Context Management")
print("=" * 60)

session_id = f"demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
context_mgr = ConversationContextManager(session_id)

# Simulate a conversation flow
prompts = [
    "I want to build a web application",
    "It should have user authentication",
    "Add a REST API for mobile apps",
    "Include real-time notifications"
]

analyzer = PromptAnalyzer()

for i, prompt in enumerate(prompts, 1):
    print(f"\nPrompt {i}: {prompt}")
    
    # Analyze with session context
    output, analysis = analyzer.analyze(prompt, session_id)
    
    # The context manager automatically saves the analysis
    print(f"  Complexity: {analysis['complexity_score']}")
    print(f"  Agents: {analysis['swarm_agents_recommended']}")

# Get accumulated context
context = context_mgr.get_recent_context()
print(f"\nAccumulated Context:")
print(f"  Recent tasks: {len(context.recent_tasks)}")
print(f"  Technologies: {', '.join(context.technologies)}")
print(f"  Active patterns: {', '.join(context.patterns)}")

# Example 3: Swarm Orchestration Commands
print("\n" + "=" * 60)
print("Example 3: Swarm Orchestration")
print("=" * 60)

# Complex task that would trigger hive mind
complex_prompt = """
Design and implement a distributed microservices architecture for a 
financial trading platform with real-time data processing, 
high-frequency trading capabilities, and regulatory compliance.
"""

output, analysis = analyzer.analyze(complex_prompt)

print(f"Task: Financial trading platform")
print(f"Complexity: {analysis['complexity_score']}/10")
print(f"Recommended approach: {'Hive Mind' if analysis['complexity_score'] >= 8 else 'Standard Swarm'}")

# Show the generated spawn command
if analysis['swarm_agents_recommended'] > 0:
    print(f"\nGenerated Command:")
    if analysis['complexity_score'] >= 8:
        print(f"npx claude-flow@alpha hive-mind spawn \"Design financial platform\" --queen-type strategic --max-workers {analysis['swarm_agents_recommended']}")
    else:
        print(f"npx claude-flow@alpha swarm \"Design financial platform\" --max-agents {analysis['swarm_agents_recommended']}")

# Example 4: Performance Analysis
print("\n" + "=" * 60)
print("Example 4: Performance Bottleneck Detection")
print("=" * 60)

# Check for bottlenecks (simulated)
bottleneck_data = cf.analyze_bottleneck(scope="system")
if bottleneck_data:
    print("Bottleneck analysis available")
else:
    print("No bottleneck data (would require active claude-flow system)")

# Example 5: Memory Namespaces
print("\n" + "=" * 60)
print("Example 5: Working with Memory Namespaces")
print("=" * 60)

namespaces = [
    "claude-conversation-" + session_id,
    "tasks-" + session_id,
    "agents-" + session_id,
    "swarm-" + session_id
]

for ns in namespaces:
    # Store example data
    cf.memory_store(
        f"example_{ns}", 
        f"Data for {ns}",
        namespace=ns
    )
    print(f"Created namespace: {ns}")

# Example 6: Agent Spawning Simulation
print("\n" + "=" * 60)
print("Example 6: Agent Spawning Recommendations")
print("=" * 60)

test_prompts = [
    ("Fix typo in README", "Simple task"),
    ("Add user authentication to API", "Moderate task"),
    ("Refactor entire codebase to microservices", "Complex task"),
    ("Build AI-powered trading system with compliance", "Enterprise task")
]

for prompt, description in test_prompts:
    _, analysis = analyzer.analyze(prompt)
    agents = analysis['swarm_agents_recommended']
    roles = analysis['recommended_agent_roles']
    
    print(f"\n{description}: '{prompt[:40]}...'")
    print(f"  Agents: {agents}")
    if roles:
        print(f"  Roles: {', '.join(roles[:3])}")
    
    # Show spawn command
    if agents > 0:
        if agents == 1:
            print(f"  Command: Use Task tool directly")
        elif agents <= 5:
            print(f"  Command: npx claude-flow@alpha swarm \"{prompt[:30]}...\" --max-agents {agents}")
        else:
            print(f"  Command: npx claude-flow@alpha hive-mind spawn \"{prompt[:30]}...\" --max-workers {agents}")

print("\n" + "=" * 60)
print("Integration Examples Complete")
print("=" * 60)