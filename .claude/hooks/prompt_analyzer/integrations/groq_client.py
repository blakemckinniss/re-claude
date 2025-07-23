"""
Groq API client integration
"""

import os
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None


@dataclass
class GroqConfig:
    """Configuration for Groq client"""
    api_key: str
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.3
    max_tokens: int = 1024
    timeout: int = 30


class GroqClient:
    """Wrapper for Groq API interactions"""
    
    def __init__(self, config: Optional[GroqConfig] = None):
        if config:
            self.config = config
        else:
            # Load from environment
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")
            
            self.config = GroqConfig(
                api_key=api_key,
                model=os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),
                temperature=float(os.getenv('GROQ_TEMPERATURE', '0.3')),
                max_tokens=int(os.getenv('GROQ_MAX_TOKENS', '1024'))
            )
        
        self.client: Optional[Any] = None
        if GROQ_AVAILABLE and Groq is not None:
            self.client = Groq(api_key=self.config.api_key)
    
    @property
    def is_available(self) -> bool:
        """Check if Groq is available"""
        return GROQ_AVAILABLE and self.client is not None
    
    def analyze_prompt(self, prompt: str, system_prompt: str, 
                      response_format: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze a prompt using Groq"""
        if not self.is_available or self.client is None:
            return self._fallback_analysis(prompt)
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            completion = self.client.chat.completions.create(
                messages=messages,
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            response_text = completion.choices[0].message.content
            if response_text:
                response_text = response_text.strip()
            else:
                response_text = ""
            
            # Try to parse JSON response
            if response_format:
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response", "raw": response_text}
            
            return {"response": response_text}
            
        except Exception as e:
            return {"error": str(e)}
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize text using Groq"""
        if not self.is_available or self.client is None:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        prompt = f"""Summarize this text in under {max_length} characters. 
Be concise and capture the key points.

Text: {text}

Summary:"""
        
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.config.model,
                temperature=0.3,
                max_tokens=100
            )
            
            summary = completion.choices[0].message.content
            if summary:
                summary = summary.strip()
            else:
                summary = ""
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            return summary
            
        except Exception:
            # Fallback to simple truncation
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def _fallback_analysis(self, prompt: str) -> Dict[str, Any]:
        """Fallback analysis when Groq is not available"""
        # Simple keyword-based analysis
        prompt_lower = prompt.lower()
        
        # Detect complexity
        complexity = 3
        if len(prompt.split()) > 50:
            complexity += 2
        if any(word in prompt_lower for word in ["complex", "enterprise", "scale"]):
            complexity += 2
        
        # Detect tech
        tech_keywords = {
            "python": ["python", "py", "django", "flask"],
            "javascript": ["javascript", "js", "node", "react", "vue"],
            "database": ["database", "sql", "postgres", "mysql"],
            "api": ["api", "rest", "graphql", "endpoint"],
            "cloud": ["aws", "azure", "gcp", "cloud"],
            "docker": ["docker", "container", "kubernetes"]
        }
        
        tech_involved = []
        for tech, keywords in tech_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                tech_involved.append(tech)
        
        return {
            "topic_genre": "general development",
            "complexity_score": min(complexity, 10),
            "tech_involved": tech_involved,
            "analysis_notes": "Groq not available - using fallback analysis",
            "swarm_agents_recommended": max(1, complexity // 2),
            "recommended_agent_roles": ["coordinator", "coder", "tester"],
            "recommended_mcp_tools": ["swarm_init", "agent_spawn", "task_orchestrate"]
        }