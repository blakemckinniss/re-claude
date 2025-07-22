#!/usr/bin/env python3
"""
Basic usage example of the modular prompt analyzer
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompt_analyzer import PromptAnalyzer
from prompt_analyzer.utils.config import Config, load_dotenv

# Load environment variables
load_dotenv()

# Example 1: Simple analysis
print("=" * 60)
print("Example 1: Simple Task Analysis")
print("=" * 60)

analyzer = PromptAnalyzer()
prompt = "Fix the bug in the login function"

output, analysis = analyzer.analyze(prompt)
print(f"Prompt: {prompt}")
print(f"\nAnalysis Output:\n{output}")
print(f"\nComplexity Score: {analysis['complexity_score']}")
print(f"Recommended Agents: {analysis['swarm_agents_recommended']}")

# Example 2: Complex task
print("\n" + "=" * 60)
print("Example 2: Complex Task Analysis")
print("=" * 60)

complex_prompt = """
Create a microservices architecture for an e-commerce platform with:
- User authentication service
- Product catalog service  
- Order management service
- Payment processing
- Real-time inventory tracking
Include Docker containers, Kubernetes deployment, and monitoring.
"""

output, analysis = analyzer.analyze(complex_prompt)
print(f"Prompt: {complex_prompt[:100]}...")
print(f"\nComplexity Score: {analysis['complexity_score']}")
print(f"Topic: {analysis['topic_genre']}")
print(f"Recommended Agents: {analysis['swarm_agents_recommended']}")
print(f"Agent Roles: {', '.join(analysis['recommended_agent_roles'])}")
print(f"Key Tools: {', '.join(analysis['recommended_mcp_tools'][:5])}")

# Example 3: With session context
print("\n" + "=" * 60)
print("Example 3: Analysis with Session Context")
print("=" * 60)

session_id = "demo-session-123"

# First prompt
prompt1 = "I'm building a REST API with Python and FastAPI"
output1, _ = analyzer.analyze(prompt1, session_id)

# Second prompt (will have context from first)
prompt2 = "Add authentication to the API"
output2, analysis2 = analyzer.analyze(prompt2, session_id)

print(f"First prompt: {prompt1}")
print(f"Second prompt: {prompt2}")
print(f"\nAnalysis includes context from previous prompt")
print(f"Detected continuation of API development task")