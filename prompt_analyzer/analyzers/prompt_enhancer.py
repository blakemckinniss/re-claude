"""
Prompt enhancement for optimal Claude Code execution
"""

import re
from typing import Dict, Any, List, Optional
from ..models.enhancement import PromptEnhancement, ExecutionInstructions, SpawnCommand
from ..models.patterns import TaskPattern
from ..models.analysis import TaskComplexity


class PromptEnhancer:
    """Enhance prompts for optimal Claude Code execution"""
    
    def __init__(self):
        self.structure_indicators = {
            'context': ['Context:', 'Background:', 'Given:', 'Current state:'],
            'objective': ['Goal:', 'Objective:', 'Task:', 'Please:', 'I need', 'Create', 'Build'],
            'constraints': ['Constraints:', 'Requirements:', 'Must:', 'Should:', 'Rules:'],
            'examples': ['Example:', 'For example:', 'e.g.', 'Such as:', 'Like:'],
            'success': ['Success criteria:', 'Done when:', 'Complete when:', 'Acceptance:']
        }
    
    def analyze_prompt_structure(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt structure and identify components"""
        lines = prompt.strip().split('\n')
        
        # Check for structural components
        structure = {}
        for component, indicators in self.structure_indicators.items():
            structure[f'has_{component}'] = any(
                any(indicator.lower() in line.lower() for indicator in indicators)
                for line in lines
            )
        
        # Check for code blocks
        structure['has_code'] = '```' in prompt or any(
            line.strip().startswith(('def ', 'class ', 'function ', 'import ', 'const ', 'let ', 'var '))
            for line in lines
        )
        
        # Check for file references
        file_patterns = r'(\.[a-zA-Z0-9]+\b|\/[a-zA-Z0-9_\-\/]+\.[a-zA-Z0-9]+|[a-zA-Z0-9_\-]+\.(py|js|ts|jsx|tsx|java|cpp|c|h|go|rs|rb|php))'
        structure['has_files'] = bool(re.search(file_patterns, prompt))
        
        # Check for URLs
        url_pattern = r'https?://[^\s]+'
        structure['has_urls'] = bool(re.search(url_pattern, prompt))
        
        # Basic metrics
        structure['line_count'] = len(lines)
        structure['word_count'] = len(prompt.split())
        structure['char_count'] = len(prompt)
        structure['is_question'] = prompt.strip().endswith('?')
        structure['is_command'] = any(
            prompt.lower().startswith(cmd) for cmd in 
            ['create', 'build', 'make', 'implement', 'write', 'generate', 'fix', 'debug']
        )
        
        return structure
    
    def enhance_prompt(self, prompt: str, analysis: Dict[str, Any], 
                      patterns: List[TaskPattern]) -> PromptEnhancement:
        """Enhance prompt for better Claude Code understanding"""
        structure = self.analyze_prompt_structure(prompt)
        
        enhanced_parts = []
        context_additions = []
        clarifications = []
        
        # Structure recommendations
        if not structure['has_objective'] and not structure['is_question']:
            clarifications.append("Consider starting with 'Task:' or 'Goal:' to clearly state the objective")
        
        if not structure['has_context'] and structure['word_count'] < 20:
            clarifications.append("Add context about the project, current state, or environment")
        
        if structure['has_files'] and not structure['has_context']:
            context_additions.append("Working with files - ensure paths are relative to project root")
        
        if structure['has_code'] and not structure['has_objective']:
            clarifications.append("Clarify what should be done with the provided code")
        
        # Pattern-based enhancements
        if patterns:
            pattern_names = [p.name.replace('_', ' ').title() for p in patterns]
            context_additions.append(f"Task Type: {', '.join(pattern_names)}")
        
        # Complexity-based structure suggestions
        structured_format = None
        complexity_score = analysis.get('complexity_score', 0)
        
        if complexity_score >= 6:
            structured_format = {
                "objective": "Primary goal or outcome",
                "context": "Current state and relevant background",
                "requirements": ["Functional requirement 1", "Functional requirement 2"],
                "constraints": ["Technical constraint 1", "Business constraint 2"],
                "success_criteria": ["Measurable criterion 1", "Testable criterion 2"],
                "preferred_approach": "Suggested methodology or architecture"
            }
            
            if not structure['has_constraints']:
                clarifications.append("Consider adding explicit constraints or requirements")
            
            if not structure['has_success']:
                clarifications.append("Define clear success criteria for complex tasks")
        
        # Build enhanced prompt
        enhanced_prompt = prompt
        
        # Add structure if missing key components
        if not structure['has_objective'] and not structure['is_question']:
            if structure['is_command']:
                enhanced_prompt = prompt  # Commands are clear enough
            else:
                enhanced_prompt = f"Task: {prompt}"
        
        # Recommend approach based on complexity and patterns
        recommended_approach = self._get_recommended_approach(
            complexity_score, patterns, structure
        )
        
        return PromptEnhancement(
            original_prompt=prompt,
            enhanced_prompt=enhanced_prompt,
            context_additions=context_additions,
            clarifications=clarifications[:3],  # Limit to top 3
            structured_format=structured_format,
            recommended_approach=recommended_approach,
            structure_analysis=structure
        )
    
    def _get_recommended_approach(self, complexity_score: int, 
                                 patterns: List[TaskPattern],
                                 structure: Dict[str, Any]) -> Optional[str]:
        """Get recommended approach based on analysis"""
        if complexity_score >= 8:
            approach = "1. Break down into subtasks using Task tool\n"
            approach += "2. Use hive mind coordination for consensus\n"
            approach += "3. Implement incrementally with checkpoints\n"
            approach += "4. Test each component thoroughly\n"
            approach += "5. Document architecture decisions"
        elif complexity_score >= 6:
            approach = "1. Plan architecture before implementation\n"
            approach += "2. Use parallel execution for independent components\n"
            approach += "3. Implement core functionality first\n"
            approach += "4. Add tests for critical paths\n"
            approach += "5. Refactor for maintainability"
        elif complexity_score >= 4:
            approach = "1. Understand requirements fully\n"
            approach += "2. Design modular components\n"
            approach += "3. Implement with clean code practices\n"
            approach += "4. Test key functionality\n"
            approach += "5. Document usage"
        else:
            # Simple tasks
            if structure['has_code']:
                approach = "Review code, make requested changes, test functionality"
            elif structure['is_question']:
                approach = "Analyze question, provide clear explanation with examples"
            else:
                approach = "Implement directly with clean, tested code"
        
        return approach
    
    def create_execution_instructions(self, analysis: Dict[str, Any], 
                                    patterns: List[TaskPattern],
                                    complexity: TaskComplexity) -> ExecutionInstructions:
        """Create specific execution instructions"""
        instructions = ExecutionInstructions()
        
        # Complexity-based instructions
        if complexity.score >= 7:
            instructions.complexity_instructions = [
                "USE HIVE MIND: This is a complex task - initialize hive mind coordination",
                "PARALLEL EXECUTION: Break into subtasks and execute in parallel",
                "CHECKPOINT FREQUENTLY: Save progress to memory after each major step"
            ]
        elif complexity.score >= 4:
            instructions.complexity_instructions = [
                "PLAN FIRST: Create a structured plan before implementation",
                "MODULAR APPROACH: Break into clear, testable components",
                "TEST INCREMENTALLY: Verify each component before proceeding"
            ]
        else:
            instructions.complexity_instructions = [
                "DIRECT IMPLEMENTATION: Task is straightforward - proceed with implementation",
                "SINGLE FOCUS: Complete the task in a focused manner",
                "VERIFY RESULT: Test the final output"
            ]
        
        # Pattern-specific instructions
        pattern_instructions = {
            "api_development": "API DESIGN: Define endpoints and data models first",
            "frontend_development": "COMPONENT STRUCTURE: Plan component hierarchy",
            "database_operations": "BACKUP FIRST: Create backups before modifications",
            "testing_automation": "COVERAGE GOALS: Aim for comprehensive test coverage",
            "performance_optimization": "BENCHMARK: Measure before and after optimization",
            "security_audit": "THOROUGH SCAN: Check all potential vulnerabilities",
            "documentation": "CLEAR STRUCTURE: Use consistent formatting and sections",
            "refactoring": "PRESERVE BEHAVIOR: Ensure functionality remains intact",
            "deployment": "ROLLBACK PLAN: Prepare rollback strategy",
            "data_analysis": "VISUALIZE: Create clear visualizations of findings",
            "architecture_design": "DIAGRAM FIRST: Create architecture diagrams",
            "debugging": "ISOLATE ISSUE: Narrow down the problem systematically"
        }
        
        for pattern in patterns[:2]:  # Top 2 patterns
            if pattern.name in pattern_instructions:
                instructions.pattern_instructions.append(
                    f"4. {pattern_instructions[pattern.name]}"
                )
        
        # Critical reminders
        instructions.critical_reminders = [
            "SPAWN AGENTS: Use Task tool for parallel execution when beneficial",
            "MEMORY USAGE: Store important context with mcp__claude-flow__memory_usage",
            "WEB SEARCH: Use WebSearch for current information needs",
            "BATCH OPERATIONS: Combine multiple operations for efficiency",
            "PROGRESS TRACKING: Update todos and provide clear status updates"
        ]
        
        return instructions
    
    def create_spawn_command(self, agent_count: int, agent_roles: List[str],
                           complexity: TaskComplexity, objective: str) -> SpawnCommand:
        """Create the appropriate spawn command"""
        if agent_count == 0:
            return SpawnCommand(
                agent_count=0,
                agent_roles=[],
                command_type="none",
                objective=""
            )
        
        # Determine command type based on complexity
        if complexity.score >= 8:
            command_type = "hive-mind"
            queen_type = "strategic" if "architect" in agent_roles else "adaptive"
            additional_params = {"queen_type": queen_type}
        else:
            command_type = "swarm"
            additional_params = {}
        
        return SpawnCommand(
            agent_count=agent_count,
            agent_roles=agent_roles,
            command_type=command_type,
            objective=objective,
            additional_params=additional_params
        )