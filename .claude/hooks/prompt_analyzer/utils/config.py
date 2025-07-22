"""
Configuration management for prompt analyzer
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration for prompt analyzer"""
    
    # API Configuration
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.3
    groq_max_tokens: int = 1024
    groq_timeout: int = 30
    
    # Claude Flow Configuration
    claude_flow_timeout: int = 30
    memory_namespace: str = "claude-conversation"
    session_ttl: int = 86400  # 24 hours
    
    # Analysis Configuration
    max_prompt_length: int = 10240
    max_patterns: int = 5
    max_agents: int = 12
    max_tools: int = 15
    
    # Logging Configuration
    log_dir: Optional[str] = None
    log_level: str = "INFO"
    log_to_stderr: bool = False
    max_log_size_mb: int = 10
    max_log_files: int = 5
    
    # Cache Configuration
    cache_duration: int = 300  # 5 minutes
    use_cache: bool = True
    
    # Feature Flags
    use_groq_summary: bool = True
    groq_summary_threshold: int = 15
    groq_summary_interval: int = 10
    auto_spawn_agents: bool = True
    enable_hive_mind: bool = True
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables"""
        return cls(
            groq_api_key=os.getenv('GROQ_API_KEY'),
            groq_model=os.getenv('GROQ_MODEL', cls.groq_model),
            groq_temperature=float(os.getenv('GROQ_TEMPERATURE', str(cls.groq_temperature))),
            groq_max_tokens=int(os.getenv('GROQ_MAX_TOKENS', str(cls.groq_max_tokens))),
            groq_timeout=int(os.getenv('GROQ_TIMEOUT', str(cls.groq_timeout))),
            
            claude_flow_timeout=int(os.getenv('CLAUDE_FLOW_TIMEOUT', str(cls.claude_flow_timeout))),
            memory_namespace=os.getenv('MEMORY_NAMESPACE', cls.memory_namespace),
            session_ttl=int(os.getenv('SESSION_TTL', str(cls.session_ttl))),
            
            max_prompt_length=int(os.getenv('MAX_PROMPT_LENGTH', str(cls.max_prompt_length))),
            max_patterns=int(os.getenv('MAX_PATTERNS', str(cls.max_patterns))),
            max_agents=int(os.getenv('MAX_AGENTS', str(cls.max_agents))),
            max_tools=int(os.getenv('MAX_TOOLS', str(cls.max_tools))),
            
            log_dir=os.getenv('LOG_DIR'),
            log_level=os.getenv('LOG_LEVEL', cls.log_level),
            log_to_stderr=os.getenv('LOG_TO_STDERR', '').lower() in ('true', '1', 'yes'),
            max_log_size_mb=int(os.getenv('MAX_LOG_SIZE_MB', str(cls.max_log_size_mb))),
            max_log_files=int(os.getenv('MAX_LOG_FILES', str(cls.max_log_files))),
            
            cache_duration=int(os.getenv('CACHE_DURATION', str(cls.cache_duration))),
            use_cache=os.getenv('USE_CACHE', '').lower() not in ('false', '0', 'no'),
            
            use_groq_summary=os.getenv('USE_GROQ_SUMMARY', '').lower() not in ('false', '0', 'no'),
            groq_summary_threshold=int(os.getenv('GROQ_SUMMARY_THRESHOLD', str(cls.groq_summary_threshold))),
            groq_summary_interval=int(os.getenv('GROQ_SUMMARY_INTERVAL', str(cls.groq_summary_interval))),
            auto_spawn_agents=os.getenv('AUTO_SPAWN_AGENTS', '').lower() not in ('false', '0', 'no'),
            enable_hive_mind=os.getenv('ENABLE_HIVE_MIND', '').lower() not in ('false', '0', 'no')
        )
    
    @classmethod
    def from_file(cls, config_file: str) -> 'Config':
        """Load config from JSON file"""
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        # Create config with defaults
        config = cls()
        
        # Update with file data
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'groq': {
                'api_key': '***' if self.groq_api_key else None,  # Hide API key
                'model': self.groq_model,
                'temperature': self.groq_temperature,
                'max_tokens': self.groq_max_tokens,
                'timeout': self.groq_timeout
            },
            'claude_flow': {
                'timeout': self.claude_flow_timeout,
                'memory_namespace': self.memory_namespace,
                'session_ttl': self.session_ttl
            },
            'analysis': {
                'max_prompt_length': self.max_prompt_length,
                'max_patterns': self.max_patterns,
                'max_agents': self.max_agents,
                'max_tools': self.max_tools
            },
            'logging': {
                'log_dir': self.log_dir,
                'log_level': self.log_level,
                'log_to_stderr': self.log_to_stderr,
                'max_log_size_mb': self.max_log_size_mb,
                'max_log_files': self.max_log_files
            },
            'cache': {
                'duration': self.cache_duration,
                'enabled': self.use_cache
            },
            'features': {
                'use_groq_summary': self.use_groq_summary,
                'groq_summary_threshold': self.groq_summary_threshold,
                'groq_summary_interval': self.groq_summary_interval,
                'auto_spawn_agents': self.auto_spawn_agents,
                'enable_hive_mind': self.enable_hive_mind
            }
        }
    
    def save(self, config_file: str):
        """Save config to JSON file"""
        with open(config_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


def load_dotenv(path: Optional[str] = None):
    """Simple dotenv loader"""
    if not path:
        path = Path.cwd() / '.env'
    else:
        path = Path(path)
    
    if path.exists():
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key.strip()] = value