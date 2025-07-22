"""
Prompt enhancement models
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class PromptEnhancement:
    """Structure for prompt enhancement suggestions"""
    original_prompt: str
    enhanced_prompt: str
    context_additions: List[str] = field(default_factory=list)
    clarifications: List[str] = field(default_factory=list)
    structured_format: Optional[Dict[str, Any]] = None
    recommended_approach: Optional[str] = None
    structure_analysis: Optional[Dict[str, bool]] = None
    
    def has_suggestions(self) -> bool:
        """Check if there are any enhancement suggestions"""
        return bool(
            self.context_additions or 
            self.clarifications or 
            self.structured_format or 
            self.recommended_approach
        )
    
    def get_formatted_suggestions(self) -> str:
        """Get formatted enhancement suggestions"""
        suggestions = []
        
        if self.clarifications:
            suggestions.append("📝 PROMPT ENHANCEMENT SUGGESTIONS:")
            for clarification in self.clarifications[:3]:
                suggestions.append(f"• {clarification}")
        
        if self.recommended_approach:
            suggestions.append(f"\n🎯 RECOMMENDED APPROACH:\n{self.recommended_approach}")
        
        if self.structured_format:
            suggestions.append("\n📋 SUGGESTED STRUCTURE:")
            for key, value in self.structured_format.items():
                if isinstance(value, list):
                    suggestions.append(f"• {key}: {', '.join(value[:2])}")
                else:
                    suggestions.append(f"• {key}: {value}")
        
        return "\n".join(suggestions) if suggestions else ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "original_prompt": self.original_prompt,
            "enhanced_prompt": self.enhanced_prompt,
            "context_additions": self.context_additions,
            "clarifications": self.clarifications,
            "structured_format": self.structured_format,
            "recommended_approach": self.recommended_approach,
            "structure_analysis": self.structure_analysis
        }


@dataclass
class ExecutionInstructions:
    """Execution instructions for Claude Code"""
    complexity_instructions: List[str] = field(default_factory=list)
    pattern_instructions: List[str] = field(default_factory=list)
    tool_instructions: List[str] = field(default_factory=list)
    critical_reminders: List[str] = field(default_factory=list)
    
    def format(self) -> str:
        """Format instructions for output"""
        sections = []
        
        if self.complexity_instructions:
            sections.append("[EXECUTION INSTRUCTIONS]")
            for i, instruction in enumerate(self.complexity_instructions, 1):
                sections.append(f"{i}. {instruction}")
        
        if self.pattern_instructions:
            for instruction in self.pattern_instructions[:2]:
                sections.append(instruction)
        
        if self.critical_reminders:
            sections.append("\n[CRITICAL REMINDERS]")
            for reminder in self.critical_reminders:
                sections.append(f"• {reminder}")
        
        return "\n".join(sections)


@dataclass
class SpawnCommand:
    """Agent spawn command information"""
    agent_count: int
    agent_roles: List[str]
    command_type: str  # "swarm" or "hive-mind"
    objective: str
    additional_params: Dict[str, Any] = field(default_factory=dict)
    
    def format(self) -> str:
        """Format spawn command"""
        if self.agent_count == 0:
            return ""
        
        if self.command_type == "hive-mind":
            queen_type = self.additional_params.get("queen_type", "adaptive")
            return f"""
🚀 HIVE MIND COMMAND: npx claude-flow@alpha hive-mind spawn "{self.objective[:50]}..." --queen-type {queen_type} --max-workers {self.agent_count}
🎭 SPECIALIZED ROLES: {', '.join(self.agent_roles)}
⚡ COORDINATION: Hive mind with consensus building"""
        else:
            return f"""
🚀 SWARM COMMAND: npx claude-flow@alpha swarm "{self.objective[:50]}..." --max-agents {self.agent_count}
🎭 AGENT ROLES: {', '.join(self.agent_roles)}
🔄 EXECUTION: Parallel coordination enabled"""