"""
Output formatting utilities
"""

from typing import Dict, Any, List, Optional
from ..models.analysis import AnalysisResult, TaskComplexity
from ..models.enhancement import PromptEnhancement, ExecutionInstructions, SpawnCommand
from ..models.patterns import TaskPattern


class OutputFormatter:
    """Format analysis output for different contexts"""
    
    @staticmethod
    def format_analysis_output(analysis: AnalysisResult, 
                             enhancement: PromptEnhancement,
                             patterns: List[TaskPattern],
                             context_summary: str) -> str:
        """Format the complete analysis output"""
        sections = []
        
        # Main analysis section
        sections.append(OutputFormatter._format_analysis_section(analysis, patterns))
        
        # Context section if available
        if context_summary and context_summary != "No previous context":
            sections.append(f"\n📜 CONVERSATION CONTEXT:\n{context_summary}")
        
        # Enhancement suggestions
        if enhancement.has_suggestions():
            sections.append(OutputFormatter._format_enhancement_section(enhancement))
        
        # Swarm orchestration if agents recommended
        if analysis.swarm_agents_recommended > 0:
            sections.append(OutputFormatter._format_swarm_section(analysis))
        
        return "\n".join(sections)
    
    @staticmethod
    def _format_analysis_section(analysis: AnalysisResult, 
                               patterns: List[TaskPattern]) -> str:
        """Format main analysis section"""
        pattern_names = [p.name.replace('_', ' ').title() for p in patterns]
        
        output = f"""
🤖 ENHANCED PROMPT ANALYSIS:
📋 Topic/Genre: {analysis.topic_genre}
🎯 Complexity: {analysis.complexity_level.name} ({analysis.complexity_score}/10)
🔧 Tech Stack: {', '.join(analysis.tech_involved) if analysis.tech_involved else 'None detected'}
📝 Task Patterns: {', '.join(pattern_names) if pattern_names else 'General task'}"""
        
        if analysis.confidence_score > 0:
            output += f"\n🎲 Confidence: {analysis.confidence_score:.1%}"
        
        output += f"\n\n💡 ANALYSIS INSIGHTS:\n{analysis.analysis_notes}"
        
        return output
    
    @staticmethod
    def _format_enhancement_section(enhancement: PromptEnhancement) -> str:
        """Format enhancement suggestions"""
        sections = []
        
        if enhancement.clarifications:
            sections.append("📝 PROMPT ENHANCEMENT SUGGESTIONS:")
            for clarification in enhancement.clarifications:
                sections.append(f"• {clarification}")
        
        if enhancement.recommended_approach:
            sections.append(f"\n🎯 RECOMMENDED APPROACH:\n{enhancement.recommended_approach}")
        
        if enhancement.structured_format:
            sections.append("\n📋 SUGGESTED STRUCTURE:")
            for key, value in enhancement.structured_format.items():
                if isinstance(value, list):
                    sections.append(f"• {key}: {', '.join(value[:2])}")
                else:
                    sections.append(f"• {key}: {value}")
        
        return "\n".join(sections)
    
    @staticmethod
    def _format_swarm_section(analysis: AnalysisResult) -> str:
        """Format swarm orchestration section"""
        output = f"""
🐝 SWARM ORCHESTRATION:
👥 Recommended Agents: {analysis.swarm_agents_recommended}
🎭 Agent Roles: {', '.join(analysis.recommended_agent_roles)}"""
        
        # Limit tool display to prevent overwhelming output
        tools = analysis.recommended_mcp_tools[:8]
        if tools:
            output += f"\n🛠️ Key MCP Tools: {', '.join(tools)}"
            if len(analysis.recommended_mcp_tools) > 8:
                output += f" (+{len(analysis.recommended_mcp_tools) - 8} more)"
        
        return output
    
    @staticmethod
    def format_execution_instructions(instructions: ExecutionInstructions) -> str:
        """Format execution instructions"""
        return instructions.format()
    
    @staticmethod
    def format_spawn_command(spawn_cmd: SpawnCommand) -> str:
        """Format spawn command"""
        return spawn_cmd.format()
    
    @staticmethod
    def format_critical_reminders() -> str:
        """Format critical reminders section"""
        return """
[CRITICAL REMINDERS]
1. ALWAYS provide clear next steps after each action
2. SPAWN agents liberally - use Task tool for parallel execution when possible
3. KEEP memories updated - use mcp__claude-flow__memory_usage to store important context
4. USE web search liberally - leverage WebSearch and WebFetch for current information
5. BATCH operations - combine multiple tool calls in single messages for efficiency
6. CLAUDE CODE EXECUTES - MCP tools coordinate, Claude Code does ALL actual work
7. NO SEQUENTIAL TodoWrite calls - batch ALL todos together
8. AGENTS MUST USE HOOKS - every agent follows the coordination protocol
9. THINK VERY HARD - Use ultrathink for complex reasoning tasks
10. ALL DOCUMENTATION NEEDS TO BE EPHEMERAL - unless requested otherwise, do not store documentation permanently
11. USE THE SWARM COMMAND - always use the npx swarm spawn command to create agents
12. ALWAYS CREATE AGENTS FOR COMPLEX TASKS - if the task is complex, spawn agents to handle it"""
    
    @staticmethod
    def format_log_entry(timestamp: str, level: str, message: str, 
                        data: Optional[Dict[str, Any]] = None) -> str:
        """Format a log entry for text output"""
        entry = f"[{timestamp}] {level}: {message}"
        
        if data:
            # Format key data points
            important_keys = ['complexity_score', 'agent_count', 'duration_ms', 'error_type']
            data_parts = []
            
            for key in important_keys:
                if key in data:
                    data_parts.append(f"{key}={data[key]}")
            
            if data_parts:
                entry += f" | {', '.join(data_parts)}"
        
        return entry
    
    @staticmethod
    def format_error_output(error: Exception, context: Dict[str, Any]) -> str:
        """Format error output for user display"""
        output = f"""
⚠️ ANALYSIS ERROR:
Type: {type(error).__name__}
Message: {str(error)}"""
        
        if context.get('fallback_used'):
            output += "\n\n📌 Using fallback analysis (Groq unavailable)"
        
        return output