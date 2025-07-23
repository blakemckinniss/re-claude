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
                             context_summary: str,
                             code_context: Optional[Dict[str, Any]] = None) -> str:
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
        
        # Prioritize context7, exa, tools in display
        priority_tools = []
        other_tools = []
        
        for tool in analysis.recommended_mcp_tools:
            if "context7" in tool or "exa" in tool in tool:
                priority_tools.append(tool)
            else:
                other_tools.append(tool)
        
        # Combine with priority tools first
        tools = priority_tools + other_tools
        display_tools = tools[:8]
        
        if display_tools:
            output += f"\n🛠️ Key MCP Tools: {', '.join(display_tools)}"
            if len(tools) > 8:
                output += f" (+{len(tools) - 8} more)"
            
            # Add emphasis for priority tools
            icons = []
            if any("context7" in t for t in priority_tools):
                icons.append("📚")
            if any("exa" in t for t in priority_tools):
                icons.append("🔍")
            
            if icons:
                output += " " + "".join(icons)
        
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
    def format_action_instruction(agent_count: int, agent_roles: List[str],
                                 task_patterns: Optional[List[str]] = None,
                                 first_action: Optional[str] = None) -> str:
        """Format the final action instruction that tells Claude what to do next"""
        # Determine the first action based on task patterns and context
        if not first_action:
            if task_patterns:
                # Pattern-specific first actions
                pattern_actions = {
                    "api_development": "design the API structure and define endpoints",
                    "frontend_development": "create the component architecture and UI flow",
                    "backend_development": "design the service architecture and data models",
                    "database_operations": "analyze the schema requirements and relationships",
                    "testing_automation": "identify test scenarios and coverage requirements",
                    "performance_optimization": "profile the current system and identify bottlenecks",
                    "security_audit": "scan for vulnerabilities and review security patterns",
                    "debugging": "reproduce the issue and gather diagnostic information",
                    "deployment": "review the deployment requirements and infrastructure",
                    "refactoring": "analyze the current code structure and identify improvements",
                    "documentation": "outline the documentation structure and key topics",
                    "architecture_design": "define system components and their interactions"
                }
                
                # Use the first matching pattern
                for pattern in task_patterns:
                    if pattern in pattern_actions:
                        first_action = pattern_actions[pattern]
                        break
            
            # Fallback based on agent count
            if not first_action:
                if agent_count >= 7:
                    first_action = "analyze the system architecture and create a comprehensive implementation plan"
                elif agent_count >= 5:
                    first_action = "break down the requirements into specific tasks and components"
                else:
                    first_action = "understand the requirements and plan the implementation approach"
        
        # Format agent roles nicely
        if agent_roles:
            roles_str = ", ".join(agent_roles[:3])
            if len(agent_roles) > 3:
                roles_str += f" (+{len(agent_roles) - 3} more)"
        else:
            roles_str = "specialized agents"
        
        # Determine todo count based on complexity
        todo_count = "8-12" if agent_count >= 7 else "5-10"
        
        instruction = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 NEXT ACTION (EXECUTE NOW):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Execute ALL of these in ONE message:
1️⃣ Initialize swarm with mcp__claude-flow__swarm_init (if complexity >= 4)
2️⃣ SPAWN {agent_count} agents ({roles_str}) using parallel Task calls
3️⃣ CREATE TodoWrite with {todo_count} todos (mixed statuses/priorities)
4️⃣ READ any relevant files mentioned in the requirements
5️⃣ THEN: {first_action}

⚡ Remember: ALL operations above in ONE message for maximum efficiency!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return instruction
    
    @staticmethod
    def format_critical_reminders() -> str:
        """Format critical reminders section"""
        return """
[CRITICAL REMINDERS]
• SEARCH FIRST: Use mcp__exa__web_search_exa for current info and best practices
• DOCS ALWAYS: Use mcp__context7__ tools for library/framework documentation
• MEMORY USAGE: Store important context with mcp__claude-flow__memory_usage
• WEB SEARCH: Use WebSearch, WebFetch, and mcp__exa__web_search_exa liberally
• BATCH OPERATIONS: Combine multiple operations for efficiency
• PROGRESS TRACKING: Update todos and provide clear status updates"""
    
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
    
    @staticmethod
    def format_mcp_injection(mcp_injection: Dict[str, Any]) -> str:
        """Format MCP injection requirements"""
        if not mcp_injection or not mcp_injection.get('required'):
            return ""
        
        enforcement_icons = {
            'suggest': '💡',
            'guide': '🎯',
            'enforce': '⚡',
            'strict': '🔥'
        }
        
        level = mcp_injection.get('enforcement_level', 'suggest')
        icon = enforcement_icons.get(level, '📌')
        
        output = f"\n{icon} MCP ENFORCEMENT ({level.upper()})"
        output += "\n" + "═" * 50
        
        if mcp_injection.get('initialization'):
            output += f"\n🚀 REQUIRED: {mcp_injection['initialization']}"
        
        # Display required MCP tools prominently
        required_tools = mcp_injection.get('required_tools', [])
        if required_tools:
            output += "\n\n🔧 MANDATORY MCP TOOLS (must use these):"
            
            # Prioritize context7 and exa tools
            priority_shown = False
            for tool in required_tools:
                if "context7" in tool:
                    output += f"\n  📚 {tool}    [DOCUMENTATION LOOKUP]"
                    priority_shown = True
                elif "exa" in tool:
                    output += f"\n  🔍 {tool}         [WEB SEARCH]"
                    priority_shown = True
            
            # Show other tools after priority ones
            other_tools = [t for t in required_tools if "context7" not in t and "exa" not in t]
            shown_count = 2 if priority_shown else 0
            
            for tool in other_tools[:max(6 - shown_count, 4)]:
                output += f"\n  🕹️ mcp__claude-flow__{tool}"
            
            if len(other_tools) > (6 - shown_count):
                output += f"\n  ... (+{len(other_tools) - (6 - shown_count)} more required tools)"
        
        if mcp_injection.get('parallel_operations'):
            output += "\n\n📦 EXECUTE IN ONE MESSAGE:"
            for op in mcp_injection['parallel_operations']:
                output += f"\n  • {op}"
        
        if level in ['enforce', 'strict']:
            output += "\n\n⛔ VIOLATIONS WILL BE BLOCKED!"
            output += "\n✅ Correct: Use ALL required MCP tools + parallel operations"
            output += "\n❌ Wrong: Skip MCP tools or use sequential operations"
        
        return output