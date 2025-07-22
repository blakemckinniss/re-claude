"""
Conversation context management with claude-flow integration
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict
from ..integrations.claude_flow import ClaudeFlowIntegration
from ..models.analysis import ConversationContext


class ConversationContextManager:
    """Enhanced conversation context management"""
    
    def __init__(self, session_id: str, memory_namespace: str = "claude-conversation"):
        self.session_id = session_id
        self.memory_namespace = memory_namespace
        self.cf = ClaudeFlowIntegration()
        self._context_cache = {}
        self._cache_timestamp = None
        self.cache_duration = 300  # 5 minutes
    
    def get_recent_context(self, max_entries: int = 20, 
                          use_cache: bool = True) -> ConversationContext:
        """Get enriched recent conversation context"""
        # Check cache
        if use_cache and self._is_cache_valid():
            return self._context_cache.get('recent_context', ConversationContext())
        
        # Query multiple memory namespaces
        namespaces = [
            f"{self.memory_namespace}-{self.session_id}",
            f"swarm-{self.session_id}",
            f"tasks-{self.session_id}",
            f"agents-{self.session_id}"
        ]
        
        all_entries = []
        for namespace in namespaces:
            entries = self._query_namespace(namespace)
            all_entries.extend(entries)
        
        # Sort by timestamp
        all_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Extract key information
        context = self._build_context_from_entries(all_entries[:max_entries])
        
        # Cache the result
        self._context_cache['recent_context'] = context
        self._cache_timestamp = datetime.now()
        
        return context
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self._cache_timestamp:
            return False
        
        age = (datetime.now() - self._cache_timestamp).total_seconds()
        return age < self.cache_duration
    
    def _query_namespace(self, namespace: str) -> List[Dict[str, Any]]:
        """Query a specific namespace"""
        return self.cf.memory_query('*', namespace)
    
    def _build_context_from_entries(self, entries: List[Dict[str, Any]]) -> ConversationContext:
        """Build context from memory entries"""
        recent_tasks = []
        technologies = set()
        patterns = []
        active_agents = set()
        
        for entry in entries:
            try:
                # Parse value if it's JSON
                value = entry.get('value', '')
                if isinstance(value, str) and value.startswith('{'):
                    try:
                        data = json.loads(value)
                    except json.JSONDecodeError:
                        data = {'raw': value}
                else:
                    data = {'raw': value}
                
                # Extract task information
                if 'task' in data or 'description' in data:
                    task = data.get('task') or data.get('description', '')
                    if task and len(task) > 10:
                        recent_tasks.append(task[:100])
                
                # Extract technologies
                if 'tech' in data or 'tech_involved' in data:
                    tech_list = data.get('tech') or data.get('tech_involved', [])
                    if isinstance(tech_list, list):
                        technologies.update(tech_list)
                
                # Extract patterns
                if 'pattern' in data or 'patterns' in data:
                    pattern_data = data.get('pattern') or data.get('patterns', [])
                    if isinstance(pattern_data, list):
                        patterns.extend(pattern_data)
                    elif isinstance(pattern_data, str):
                        patterns.append(pattern_data)
                
                # Extract agent information
                if 'agents' in data or 'agent_roles' in data:
                    agent_list = data.get('agents') or data.get('agent_roles', [])
                    if isinstance(agent_list, list):
                        active_agents.update(agent_list)
                
            except Exception:
                # Skip problematic entries
                continue
        
        return ConversationContext(
            recent_tasks=recent_tasks[:5],
            technologies=sorted(list(technologies))[:10],
            patterns=patterns[:3],
            active_agents=sorted(list(active_agents)),
            entry_count=len(entries),
            session_id=self.session_id
        )
    
    def save_analysis_context(self, analysis: Dict[str, Any], 
                            patterns: List[Any],
                            prompt: str):
        """Save analysis context for future reference"""
        timestamp = datetime.now().isoformat()
        
        # Save to task namespace
        task_entry = {
            'timestamp': timestamp,
            'prompt': prompt[:200],  # Truncate for storage
            'complexity': analysis.get('complexity_score', 0),
            'topic': analysis.get('topic_genre', 'unknown'),
            'tech': analysis.get('tech_involved', []),
            'agents': analysis.get('recommended_agent_roles', []),
            'patterns': [p.name for p in patterns] if patterns else [],
            'agent_count': analysis.get('swarm_agents_recommended', 0)
        }
        
        key = f"task_analysis_{timestamp.replace(':', '-').replace('.', '-')}"
        self.cf.memory_store(
            key, 
            json.dumps(task_entry), 
            namespace=f"tasks-{self.session_id}"
        )
        
        # Also save a summary to the main conversation namespace
        summary_entry = {
            'timestamp': timestamp,
            'type': 'analysis',
            'complexity': analysis.get('complexity_score', 0),
            'topic': analysis.get('topic_genre', 'unknown')
        }
        
        self.cf.memory_store(
            f"analysis_{timestamp.replace(':', '-').replace('.', '-')}",
            json.dumps(summary_entry),
            namespace=f"{self.memory_namespace}-{self.session_id}"
        )
    
    def save_conversation_turn(self, prompt: str, response: Optional[str] = None):
        """Save a conversation turn"""
        timestamp = datetime.now().isoformat()
        
        turn_data = {
            'timestamp': timestamp,
            'prompt': prompt[:500],  # Truncate for storage
            'response': response[:500] if response else None,
            'session_id': self.session_id
        }
        
        key = f"turn_{timestamp.replace(':', '-').replace('.', '-')}"
        self.cf.memory_store(
            key,
            json.dumps(turn_data),
            namespace=f"{self.memory_namespace}-{self.session_id}"
        )
    
    def get_session_summary(self, use_groq: bool = False) -> str:
        """Get a summary of the session"""
        context = self.get_recent_context()
        
        if use_groq:
            # TODO: Implement Groq-based summarization
            pass
        
        return context.to_summary()
    
    def get_active_agents(self) -> List[str]:
        """Get list of currently active agents"""
        # Query agent namespace
        agent_entries = self._query_namespace(f"agents-{self.session_id}")
        
        active_agents = set()
        for entry in agent_entries:
            try:
                value = entry.get('value', '')
                if isinstance(value, str) and value.startswith('{'):
                    data = json.loads(value)
                    if data.get('status') == 'active':
                        agent_name = data.get('name') or data.get('type', 'unknown')
                        active_agents.add(agent_name)
            except:
                continue
        
        return sorted(list(active_agents))
    
    def clear_cache(self):
        """Clear the context cache"""
        self._context_cache = {}
        self._cache_timestamp = None