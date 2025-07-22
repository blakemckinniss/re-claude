"""
Logging utilities for prompt analyzer
"""

import os
import sys
import json
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Dict


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    """Enhanced logger with file rotation and structured logging"""
    
    def __init__(self, name: str, log_dir: Optional[str] = None, 
                 max_file_size_mb: int = 10, max_files: int = 5):
        self.name = name
        self.log_dir = Path(log_dir) if log_dir else Path.home() / ".claude" / "logs"
        self.max_file_size_mb = max_file_size_mb
        self.max_files = max_files
        self.log_file: Optional[Path] = None
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Ensure log directory exists"""
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_log_file(self) -> Path:
        """Get current log file, rotating if needed"""
        if not self.log_file:
            self.log_file = self.log_dir / f"{self.name}.log"
        
        # Check if rotation is needed
        if self.log_file.exists():
            size_mb = self.log_file.stat().st_size / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                self._rotate_logs()
        
        return self.log_file
    
    def _rotate_logs(self):
        """Rotate log files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_name = self.log_dir / f"{self.name}.{timestamp}.log"
        
        # Rename current log
        if self.log_file.exists():
            self.log_file.rename(archive_name)
        
        # Clean up old logs
        log_pattern = f"{self.name}.*.log"
        old_logs = sorted(self.log_dir.glob(log_pattern), reverse=True)
        
        for old_log in old_logs[self.max_files:]:
            try:
                old_log.unlink()
            except:
                pass
    
    def _format_entry(self, level: LogLevel, message: str, 
                     data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Format log entry"""
        return {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "logger": self.name,
            "message": message,
            "data": data or {}
        }
    
    def log(self, level: LogLevel, message: str, 
            data: Optional[Dict[str, Any]] = None, 
            to_stderr: bool = False):
        """Log a message"""
        entry = self._format_entry(level, message, data)
        
        # Write to file
        try:
            log_file = self._get_log_file()
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            # Fallback to stderr
            print(f"Logging error: {e}", file=sys.stderr)
        
        # Also write to stderr if requested or error level
        if to_stderr or level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            formatted = f"[{entry['timestamp']}] {level.value}: {message}"
            if data:
                formatted += f" | {json.dumps(data)}"
            print(formatted, file=sys.stderr)
    
    def debug(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self.log(LogLevel.DEBUG, message, data)
    
    def info(self, message: str, data: Optional[Dict[str, Any]] = None, 
             to_stderr: bool = False):
        """Log info message"""
        self.log(LogLevel.INFO, message, data, to_stderr)
    
    def warning(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self.log(LogLevel.WARNING, message, data)
    
    def error(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self.log(LogLevel.ERROR, message, data)
    
    def critical(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        self.log(LogLevel.CRITICAL, message, data)
    
    def log_analysis(self, prompt: str, analysis: Dict[str, Any], 
                    duration_ms: Optional[int] = None):
        """Log prompt analysis results"""
        data = {
            "prompt_length": len(prompt),
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "complexity_score": analysis.get("complexity_score", 0),
            "topic": analysis.get("topic_genre", "unknown"),
            "agent_count": analysis.get("swarm_agents_recommended", 0),
            "patterns": analysis.get("task_patterns", []),
            "duration_ms": duration_ms
        }
        
        self.info("Prompt analysis completed", data)
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """Log error with context"""
        data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        self.error(f"Error occurred: {type(error).__name__}", data)