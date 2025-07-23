"""
Main prompt analyzer that orchestrates all components
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from ..models.analysis import AnalysisResult, TaskComplexity
from ..models.enhancement import PromptEnhancement
from ..models.patterns import TaskPattern
from ..analyzers.task_analyzer import TaskAnalyzer
from ..analyzers.prompt_enhancer import PromptEnhancer
from ..analyzers.context_manager import ConversationContextManager
from ..integrations.claude_flow import ClaudeFlowIntegration
from ..integrations.groq_client import GroqClient, GroqConfig
from ..utils.logging import Logger
from ..utils.formatting import OutputFormatter
from ..utils.config import Config


class PromptAnalyzer:
    """Enhanced prompt analyzer with claude-flow integration"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the prompt analyzer"""
        self.config = config or Config.from_env()
        
        # Initialize components
        self.task_analyzer = TaskAnalyzer()
        self.prompt_enhancer = PromptEnhancer()
        self.claude_flow = ClaudeFlowIntegration(timeout=self.config.claude_flow_timeout)
        self.logger = Logger("prompt_analyzer", log_dir=self.config.log_dir)
        self.formatter = OutputFormatter()
        
        # Initialize Groq client if available
        self.groq_client = None
        if self.config.groq_api_key:
            groq_config = GroqConfig(
                api_key=self.config.groq_api_key,
                model=self.config.groq_model,
                temperature=self.config.groq_temperature,
                max_tokens=self.config.groq_max_tokens,
                timeout=self.config.groq_timeout
            )
            self.groq_client = GroqClient(groq_config)
    
    def analyze(self, prompt: str, session_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze a prompt and return formatted output and analysis data
        
        Returns:
            Tuple of (formatted_output, analysis_data)
        """
        start_time = time.time()
        
        # Generate session ID if not provided
        if not session_id:
            session_id = f"claude-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Initialize context manager
        context_mgr = ConversationContextManager(session_id, self.config.memory_namespace)
        
        try:
            # Validate prompt
            if not prompt or len(prompt.strip()) < 3:
                return "", {"error": "Prompt too short"}
            
            # Truncate if too long
            if len(prompt) > self.config.max_prompt_length:
                prompt = prompt[:self.config.max_prompt_length] + "... [truncated]"
            
            # Get conversation context
            context = context_mgr.get_recent_context(use_cache=self.config.use_cache)
            context_summary = context.to_summary()
            
            # Perform task analysis
            task_analysis = self.task_analyzer.analyze_prompt(prompt)
            patterns = task_analysis['patterns']
            complexity = task_analysis['complexity']
            
            # Use Groq for enhanced analysis if available
            if self.groq_client and self.groq_client.is_available:
                groq_result = self._analyze_with_groq(prompt, context_summary, task_analysis)
                # Merge Groq insights with local analysis
                analysis_data = self._merge_analysis_results(task_analysis, groq_result)
            else:
                # Use local analysis only
                analysis_data = self._create_analysis_result(task_analysis)
            
            # Create AnalysisResult object
            analysis_result = AnalysisResult(
                topic_genre=analysis_data.get('topic_genre', 'Unknown'),
                complexity_score=analysis_data.get('complexity_score', complexity.score),
                complexity_level=complexity,
                tech_involved=analysis_data.get('tech_involved', []),
                analysis_notes=analysis_data.get('analysis_notes', ''),
                swarm_agents_recommended=analysis_data.get('swarm_agents_recommended', 0),
                recommended_agent_roles=analysis_data.get('recommended_agent_roles', []),
                recommended_mcp_tools=analysis_data.get('recommended_mcp_tools', []),
                task_patterns=[p.name for p in patterns],
                confidence_score=analysis_data.get('confidence_score', 0.8)
            )
            
            # Enhance the prompt
            enhancement = self.prompt_enhancer.enhance_prompt(
                prompt, 
                analysis_result.to_dict(), 
                patterns
            )
            
            # Create execution instructions
            instructions = self.prompt_enhancer.create_execution_instructions(
                analysis_result.to_dict(),
                patterns,
                complexity
            )
            
            # Create spawn command
            spawn_command = self.prompt_enhancer.create_spawn_command(
                analysis_result.swarm_agents_recommended,
                analysis_result.recommended_agent_roles,
                complexity,
                prompt[:100]
            )
            
            # Save analysis context
            context_mgr.save_analysis_context(
                analysis_result.to_dict(),
                patterns,
                prompt
            )
            
            # Format output
            formatted_output = self._format_complete_output(
                analysis_result,
                enhancement,
                patterns,
                context_summary,
                instructions,
                spawn_command,
                analysis_data.get('mcp_injection', {})
            )
            
            # Log analysis
            duration_ms = int((time.time() - start_time) * 1000)
            self.logger.log_analysis(prompt, analysis_result.to_dict(), duration_ms)
            
            return formatted_output, analysis_result.to_dict()
            
        except Exception as e:
            # Log error
            self.logger.log_error_with_context(e, {
                'prompt_length': len(prompt),
                'session_id': session_id
            })
            
            # Return error output
            error_output = self.formatter.format_error_output(e, {'fallback_used': True})
            return error_output, {"error": str(e)}
    
    def _analyze_with_groq(self, prompt: str, context_summary: str, 
                          task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze prompt using Groq API"""
        # Build system prompt
        system_prompt = self._build_groq_system_prompt(context_summary)
        
        # Build analysis prompt
        analysis_prompt = self._build_groq_analysis_prompt(prompt, task_analysis)
        
        # Get Groq analysis
        if self.groq_client:
            result = self.groq_client.analyze_prompt(
                analysis_prompt,
                system_prompt,
                response_format={"type": "json"}
            )
            return result
        
        return {"error": "Groq client not available"}
    
    def _build_groq_system_prompt(self, context_summary: str) -> str:
        """Build system prompt for Groq"""
        base_prompt = """You are an expert prompt analyzer for Claude Code. 
Analyze prompts to determine complexity, required agents, and optimal approach.
Consider the conversation context when making recommendations."""
        
        if context_summary and context_summary != "No previous context":
            base_prompt += f"\n\nConversation Context: {context_summary}"
        
        return base_prompt
    
    def _build_groq_analysis_prompt(self, prompt: str, 
                                   task_analysis: Dict[str, Any]) -> str:
        """Build analysis prompt for Groq"""
        patterns = task_analysis.get('patterns', [])
        pattern_names = [p.name for p in patterns] if patterns else []
        
        return f"""Analyze this prompt and provide a JSON response with MANDATORY MCP enforcement:
{{
    "topic_genre": "brief classification",
    "complexity_score": 1-10,
    "tech_involved": ["list", "of", "technologies"],
    "analysis_notes": "insightful analysis",
    "swarm_agents_recommended": 0-12,
    "recommended_agent_roles": ["specific", "roles"],
    "recommended_mcp_tools": ["tool", "names"],
    "confidence_score": 0.0-1.0,
    "mcp_injection": {{
        "required": true/false,
        "initialization": "mcp__claude-flow__swarm_init parameters",
        "parallel_operations": ["list of operations to execute in ONE message"],
        "enforcement_level": "suggest/guide/enforce/strict"
    }}
}}

CRITICAL RULES FOR MCP INJECTION:
1. If complexity_score >= 4, set mcp_injection.required = true
2. ALWAYS recommend parallel execution in ONE message
3. Include swarm_init for complexity >= 6
4. Enforce batch operations (TodoWrite 5-10+, multiple Tasks, etc.)
5. For complexity >= 8, use "strict" enforcement

Initial Analysis:
- Patterns detected: {', '.join(pattern_names)}
- Base complexity: {task_analysis.get('complexity_score', 0)}
- Initial agents: {task_analysis.get('agent_count', 0)}

User Prompt: "{prompt}"

Provide analysis with MANDATORY claude-flow patterns for parallel execution."""
    
    def _merge_analysis_results(self, local: Dict[str, Any], 
                               groq: Dict[str, Any]) -> Dict[str, Any]:
        """Merge local and Groq analysis results"""
        # Start with local analysis
        merged = local.copy()
        
        # Override with Groq insights if available
        if not groq.get('error'):
            merged.update({
                'topic_genre': groq.get('topic_genre', local.get('topic_genre', 'Unknown')),
                'complexity_score': groq.get('complexity_score', local.get('complexity_score', 3)),
                'tech_involved': groq.get('tech_involved', local.get('tech_involved', [])),
                'analysis_notes': groq.get('analysis_notes', 'Analysis completed'),
                'swarm_agents_recommended': groq.get('swarm_agents_recommended', local.get('agent_count', 0)),
                'recommended_agent_roles': groq.get('recommended_agent_roles', local.get('agent_roles', [])),
                'recommended_mcp_tools': groq.get('recommended_mcp_tools', local.get('mcp_tools', [])),
                'confidence_score': groq.get('confidence_score', 0.8),
                'mcp_injection': groq.get('mcp_injection', self._get_default_mcp_injection(local))
            })
            # Add required tools to MCP injection
            if 'required_mcp_tools' in local:
                merged['mcp_injection']['required_tools'] = local['required_mcp_tools']
        else:
            # No Groq response, add default MCP injection based on complexity
            merged['mcp_injection'] = self._get_default_mcp_injection(local)
            # Add required tools
            if 'required_mcp_tools' in local:
                merged['mcp_injection']['required_tools'] = local['required_mcp_tools']
        
        return merged
    
    def _get_default_mcp_injection(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get default MCP injection requirements based on complexity"""
        complexity = analysis.get('complexity_score', 3)
        agent_count = analysis.get('agent_count', 0)
        required_tools = analysis.get('required_mcp_tools', [])
        
        if complexity >= 6:
            return {
                'required': True,
                'initialization': f'mcp__claude-flow__swarm_init(topology="hierarchical", maxAgents={agent_count})',
                'required_tools': required_tools,
                'parallel_operations': [
                    f'Task spawning {agent_count} agents in ONE message',
                    'TodoWrite with 8-12 items in ONE call',
                    'All file operations batched together',
                    'Memory operations for context storage'
                ],
                'enforcement_level': 'strict' if complexity >= 8 else 'enforce'
            }
        elif complexity >= 4:
            return {
                'required': True,
                'initialization': f'mcp__claude-flow__swarm_init(topology="mesh", maxAgents={agent_count})',
                'required_tools': required_tools,
                'parallel_operations': [
                    f'Task spawning {agent_count} agents in parallel',
                    'TodoWrite with 5-10 items',
                    'Batch file reads together'
                ],
                'enforcement_level': 'guide'
            }
        else:
            return {
                'required': False,
                'initialization': '',
                'required_tools': [],
                'parallel_operations': ['Direct implementation'],
                'enforcement_level': 'suggest'
            }
    
    def _create_analysis_result(self, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create analysis result from local analysis only"""
        patterns = task_analysis.get('patterns', [])
        pattern_names = [p.name.replace('_', ' ').title() for p in patterns]
        
        return {
            'topic_genre': pattern_names[0] if pattern_names else 'General Task',
            'complexity_score': task_analysis.get('complexity_score', 3),
            'tech_involved': task_analysis.get('tech_involved', []),
            'analysis_notes': f"Local analysis: {len(patterns)} patterns detected",
            'swarm_agents_recommended': task_analysis.get('agent_count', 0),
            'recommended_agent_roles': task_analysis.get('agent_roles', []),
            'recommended_mcp_tools': task_analysis.get('mcp_tools', []),
            'confidence_score': 0.7  # Lower confidence for local-only
        }
    
    def _format_complete_output(self, analysis: AnalysisResult,
                               enhancement: PromptEnhancement,
                               patterns: list,
                               context_summary: str,
                               instructions: Any,
                               spawn_command: Any,
                               mcp_injection: Dict[str, Any]) -> str:
        """Format the complete output"""
        sections = []
        
        # Main analysis
        sections.append(self.formatter.format_analysis_output(
            analysis, enhancement, patterns, context_summary
        ))
        
        # MCP injection requirements (high priority)
        if mcp_injection:
            mcp_output = self.formatter.format_mcp_injection(mcp_injection)
            if mcp_output:
                sections.append(mcp_output)
        
        # Execution instructions
        if instructions:
            sections.append("\n" + instructions.format())
        
        # Critical reminders
        sections.append(self.formatter.format_critical_reminders())
        
        # Spawn command
        if spawn_command and spawn_command.agent_count > 0:
            sections.append(spawn_command.format())
        
        # FINAL ACTION INSTRUCTION - Always at the end
        action_instruction = self.formatter.format_action_instruction(
            analysis.swarm_agents_recommended,
            analysis.recommended_agent_roles,
            analysis.task_patterns  # Pass patterns for context-aware first action
        )
        sections.append(action_instruction)
        
        return "\n".join(sections)