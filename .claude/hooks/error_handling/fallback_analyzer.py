"""
Fallback analyzer for when primary analysis services fail
"""

import re
import os
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
from pathlib import Path


class SimplePatternDetector:
    """Basic pattern detection using keyword matching"""
    
    PATTERN_KEYWORDS = {
        'api_development': [
            'api', 'endpoint', 'rest', 'graphql', 'webhook', 'microservice'
        ],
        'frontend_development': [
            'react', 'vue', 'angular', 'frontend', 'ui', 'component', 'css', 'html'
        ],
        'backend_development': [
            'server', 'backend', 'service', 'database', 'auth', 'middleware'
        ],
        'database_operations': [
            'database', 'sql', 'postgres', 'mysql', 'migration', 'schema', 'query'
        ],
        'testing_automation': [
            'test', 'testing', 'qa', 'coverage', 'unit test', 'integration'
        ],
        'performance_optimization': [
            'performance', 'optimize', 'speed', 'bottleneck', 'cache', 'benchmark'
        ],
        'security_audit': [
            'security', 'audit', 'vulnerability', 'penetration', 'encryption'
        ],
        'debugging': [
            'debug', 'error', 'bug', 'issue', 'troubleshoot', 'fix'
        ],
        'deployment': [
            'deploy', 'deployment', 'ci', 'cd', 'docker', 'kubernetes', 'aws'
        ],
        'refactoring': [
            'refactor', 'cleanup', 'restructure', 'improve', 'modernize'
        ],
        'documentation': [
            'documentation', 'docs', 'readme', 'guide', 'manual', 'comment'
        ],
        'architecture_design': [
            'architecture', 'design', 'structure', 'pattern', 'framework'
        ]
    }
    
    def detect(self, text: str) -> List[str]:
        """Detect patterns in text using keyword matching"""
        text_lower = text.lower()
        detected_patterns = []
        
        for pattern, keywords in self.PATTERN_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            # Require at least 1 keyword match for pattern detection
            if score > 0:
                detected_patterns.append(pattern)
        
        # Sort by relevance (number of keyword matches)
        pattern_scores = {}
        for pattern in detected_patterns:
            keywords = self.PATTERN_KEYWORDS[pattern]
            pattern_scores[pattern] = sum(1 for kw in keywords if kw in text_lower)
        
        sorted_patterns = sorted(
            detected_patterns, 
            key=lambda p: pattern_scores[p], 
            reverse=True
        )
        
        return sorted_patterns[:3]  # Return top 3 patterns


class BasicComplexityCalculator:
    """Simple complexity calculation using heuristics"""
    
    COMPLEXITY_INDICATORS = {
        'high': [
            'complex', 'enterprise', 'distributed', 'microservice', 'scale',
            'architecture', 'system', 'integration', 'orchestration'
        ],
        'medium': [
            'implement', 'build', 'create', 'develop', 'design', 'setup',
            'configure', 'optimize', 'enhance'
        ],
        'low': [
            'simple', 'basic', 'fix', 'update', 'modify', 'change', 'add'
        ]
    }
    
    def calculate(self, text: str, patterns: List[str] = None) -> int:
        """Calculate complexity score (1-10)"""
        text_lower = text.lower()
        words = text.split()
        
        # Base complexity from text length
        base_complexity = min(len(words) // 20 + 1, 4)
        
        # Adjust based on complexity indicators
        complexity_adjustment = 0
        
        for level, indicators in self.COMPLEXITY_INDICATORS.items():
            matches = sum(1 for indicator in indicators if indicator in text_lower)
            if level == 'high' and matches > 0:
                complexity_adjustment += matches * 2
            elif level == 'medium' and matches > 0:
                complexity_adjustment += matches
            elif level == 'low' and matches > 0:
                complexity_adjustment -= matches
        
        # Adjust based on patterns
        if patterns:
            pattern_complexity = {
                'architecture_design': 3,
                'performance_optimization': 2,
                'security_audit': 2,
                'api_development': 2,
                'testing_automation': 1,
                'deployment': 1,
                'debugging': 1,
                'refactoring': 1,
                'documentation': -1
            }
            
            for pattern in patterns:
                complexity_adjustment += pattern_complexity.get(pattern, 0)
        
        # Technical keywords boost
        tech_keywords = [
            'algorithm', 'concurrent', 'async', 'parallel', 'optimization',
            'machine learning', 'ai', 'blockchain', 'encryption'
        ]
        tech_boost = sum(1 for keyword in tech_keywords if keyword in text_lower)
        
        final_complexity = base_complexity + complexity_adjustment + tech_boost
        return max(1, min(final_complexity, 10))


class FallbackAnalyzer:
    """Lightweight analyzer for when primary services fail"""
    
    def __init__(self):
        self.pattern_detector = SimplePatternDetector()
        self.complexity_calculator = BasicComplexityCalculator()
        
        # Agent role mappings
        self.pattern_agent_map = {
            'api_development': ['architect', 'coder', 'tester'],
            'frontend_development': ['designer', 'coder', 'tester'],
            'backend_development': ['architect', 'coder', 'tester'],
            'database_operations': ['analyst', 'coder', 'tester'],
            'testing_automation': ['tester', 'coder', 'reviewer'],
            'performance_optimization': ['optimizer', 'analyst', 'tester'],
            'security_audit': ['reviewer', 'analyst', 'tester'],
            'debugging': ['analyst', 'coder', 'tester'],
            'deployment': ['coordinator', 'coder', 'optimizer'],
            'refactoring': ['reviewer', 'coder', 'architect'],
            'documentation': ['documenter', 'reviewer', 'coordinator'],
            'architecture_design': ['architect', 'coordinator', 'reviewer']
        }
    
    def analyze(self, prompt: str, session_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Simplified analysis using local resources only"""
        # Detect patterns
        patterns = self.pattern_detector.detect(prompt)
        
        # Calculate complexity
        complexity = self.complexity_calculator.calculate(prompt, patterns)
        
        # Generate agent recommendations
        agent_count = self._calculate_agent_count(complexity, patterns)
        agent_roles = self._select_agent_roles(patterns, agent_count)
        
        # Extract basic technology information
        tech_involved = self._extract_technologies(prompt)
        
        # Generate basic MCP tools
        mcp_tools = self._get_basic_mcp_tools(complexity, patterns)
        
        analysis_data = {
            "topic_genre": patterns[0].replace('_', ' ').title() if patterns else "General Task",
            "complexity_score": complexity,
            "tech_involved": tech_involved,
            "analysis_notes": f"Fallback analysis - {len(patterns)} patterns detected",
            "swarm_agents_recommended": agent_count,
            "recommended_agent_roles": agent_roles,
            "recommended_mcp_tools": mcp_tools,
            "confidence_score": 0.6,
            "fallback_mode": True,
            "patterns_detected": patterns
        }
        
        formatted_output = self._format_fallback_output(analysis_data, prompt)
        return formatted_output, analysis_data
    
    def _calculate_agent_count(self, complexity: int, patterns: List[str]) -> int:
        """Calculate recommended agent count"""
        base_agents = max(complexity // 2, 2)
        
        # Adjust based on patterns
        pattern_adjustments = {
            'architecture_design': 2,
            'performance_optimization': 1,
            'api_development': 1,
            'security_audit': 1,
            'testing_automation': 1
        }
        
        adjustment = sum(pattern_adjustments.get(p, 0) for p in patterns)
        return min(max(base_agents + adjustment, 3), 10)
    
    def _select_agent_roles(self, patterns: List[str], agent_count: int) -> List[str]:
        """Select appropriate agent roles based on patterns"""
        # Start with default balanced team
        default_roles = ['coordinator', 'coder', 'tester', 'reviewer', 'analyst']
        
        # Add pattern-specific roles
        pattern_roles = set()
        for pattern in patterns:
            if pattern in self.pattern_agent_map:
                pattern_roles.update(self.pattern_agent_map[pattern])
        
        # Combine and prioritize
        combined_roles = list(pattern_roles) + default_roles
        
        # Remove duplicates while preserving order
        unique_roles = []
        seen = set()
        for role in combined_roles:
            if role not in seen:
                unique_roles.append(role)
                seen.add(role)
        
        return unique_roles[:agent_count]
    
    def _extract_technologies(self, prompt: str) -> List[str]:
        """Extract technology mentions from prompt"""
        tech_patterns = {
            'python': r'\b(python|py|django|flask|fastapi)\b',
            'javascript': r'\b(javascript|js|node|react|vue|angular)\b',
            'database': r'\b(postgres|mysql|mongodb|redis|sql)\b',
            'cloud': r'\b(aws|azure|gcp|cloud|docker|kubernetes)\b',
            'web': r'\b(html|css|http|https|api|rest)\b'
        }
        
        prompt_lower = prompt.lower()
        technologies = []
        
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                technologies.append(tech)
        
        return technologies
    
    def _get_basic_mcp_tools(self, complexity: int, patterns: List[str]) -> List[str]:
        """Get basic MCP tool recommendations"""
        base_tools = ['memory_usage']
        
        if complexity >= 4:
            base_tools.extend(['swarm_init', 'agent_spawn'])
        
        if complexity >= 6:
            base_tools.extend(['task_orchestrate', 'performance_report'])
        
        # Pattern-specific tools
        pattern_tools = {
            'performance_optimization': ['bottleneck_analyze', 'benchmark_run'],
            'security_audit': ['security_scan'],
            'deployment': ['workflow_create', 'automation_setup'],
            'testing_automation': ['quality_assess'],
            'architecture_design': ['topology_optimize']
        }
        
        for pattern in patterns:
            if pattern in pattern_tools:
                base_tools.extend(pattern_tools[pattern])
        
        # Remove duplicates
        return list(set(base_tools))
    
    def _format_fallback_output(self, analysis_data: Dict[str, Any], prompt: str) -> str:
        """Format output for fallback mode"""
        complexity = analysis_data['complexity_score']
        agent_count = analysis_data['swarm_agents_recommended'] 
        patterns = analysis_data.get('patterns_detected', [])
        
        output = f"""
⚠️  FALLBACK ANALYSIS MODE
════════════════════════════════════════════════

🔧 Primary analyzer unavailable - using local analysis
📊 Confidence: {analysis_data['confidence_score']:.1f} (reduced accuracy)
🎯 Task Type: {analysis_data['topic_genre']}
💡 Complexity: {complexity}/10 ({'High' if complexity >= 7 else 'Medium' if complexity >= 4 else 'Low'})

📋 DETECTED PATTERNS:"""
        
        if patterns:
            for i, pattern in enumerate(patterns[:3], 1):
                formatted_pattern = pattern.replace('_', ' ').title()
                output += f"\n{i}. {formatted_pattern}"
        else:
            output += "\n• General development task"
        
        if analysis_data.get('tech_involved'):
            output += f"\n\n🔧 Technologies: {', '.join(analysis_data['tech_involved'])}"
        
        output += f"""

👥 RECOMMENDED TEAM ({agent_count} agents):"""
        
        for i, role in enumerate(analysis_data['recommended_agent_roles'][:agent_count], 1):
            output += f"\n{i}. {role.title()}"
        
        if complexity >= 4:
            output += f"""

🚀 MCP COORDINATION REQUIRED:
• Initialize swarm: mcp__claude-flow__swarm_init
• Spawn {agent_count} agents in parallel
• Use memory for coordination"""
        
        output += """

⚡ FALLBACK MODE LIMITATIONS:
• Reduced analysis accuracy
• Basic pattern detection only
• Conservative recommendations
• Manual verification suggested

💡 NEXT STEPS:
1. Verify analysis matches your needs
2. Adjust agent count if necessary
3. Proceed with implementation
4. Monitor for analyzer recovery"""
        
        return output