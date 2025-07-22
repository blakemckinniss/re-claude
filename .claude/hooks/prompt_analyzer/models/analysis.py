"""
Analysis result models and enums
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class TaskComplexity(Enum):
    """Task complexity levels with associated agent counts"""
    TRIVIAL = (1, 0)      # complexity score, agent count
    SIMPLE = (2, 1)
    BASIC = (3, 2)
    MODERATE = (4, 3)
    INTERMEDIATE = (5, 4)
    COMPLEX = (6, 5)
    ADVANCED = (7, 6)
    SOPHISTICATED = (8, 8)
    ENTERPRISE = (9, 10)
    EXTREME = (10, 12)
    
    @property
    def score(self) -> int:
        """Get complexity score"""
        return self.value[0]
    
    @property
    def agent_count(self) -> int:
        """Get recommended agent count"""
        return self.value[1]
    
    @classmethod
    def from_score(cls, score: int) -> 'TaskComplexity':
        """Get complexity level from score"""
        score = max(1, min(10, score))
        for complexity in cls:
            if complexity.score >= score:
                return complexity
        return cls.EXTREME


@dataclass
class AnalysisResult:
    """Result of prompt analysis"""
    topic_genre: str
    complexity_score: int
    complexity_level: TaskComplexity
    tech_involved: List[str] = field(default_factory=list)
    analysis_notes: str = ""
    swarm_agents_recommended: int = 0
    recommended_agent_roles: List[str] = field(default_factory=list)
    recommended_mcp_tools: List[str] = field(default_factory=list)
    task_patterns: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "topic_genre": self.topic_genre,
            "complexity_score": self.complexity_score,
            "complexity_level": self.complexity_level.name,
            "tech_involved": self.tech_involved,
            "analysis_notes": self.analysis_notes,
            "swarm_agents_recommended": self.swarm_agents_recommended,
            "recommended_agent_roles": self.recommended_agent_roles,
            "recommended_mcp_tools": self.recommended_mcp_tools,
            "task_patterns": self.task_patterns,
            "confidence_score": self.confidence_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """Create from dictionary"""
        complexity_level = TaskComplexity[data.get("complexity_level", "MODERATE")]
        return cls(
            topic_genre=data.get("topic_genre", "unknown"),
            complexity_score=data.get("complexity_score", 4),
            complexity_level=complexity_level,
            tech_involved=data.get("tech_involved", []),
            analysis_notes=data.get("analysis_notes", ""),
            swarm_agents_recommended=data.get("swarm_agents_recommended", 0),
            recommended_agent_roles=data.get("recommended_agent_roles", []),
            recommended_mcp_tools=data.get("recommended_mcp_tools", []),
            task_patterns=data.get("task_patterns", []),
            confidence_score=data.get("confidence_score", 0.0)
        )


@dataclass
class ConversationContext:
    """Conversation context information"""
    recent_tasks: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    active_agents: List[str] = field(default_factory=list)
    entry_count: int = 0
    session_id: str = ""
    
    def to_summary(self, max_length: int = 200) -> str:
        """Generate a summary string"""
        parts = []
        
        if self.recent_tasks:
            parts.append(f"Tasks: {', '.join(self.recent_tasks[:3])}")
        
        if self.technologies:
            parts.append(f"Tech: {', '.join(self.technologies[:5])}")
        
        if self.active_agents:
            parts.append(f"Agents: {len(self.active_agents)} active")
        
        summary = " | ".join(parts) if parts else "No previous context"
        
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary