"""
Error tracking and metrics for analyzer health monitoring
"""

import time
import json
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisError(Exception):
    """Base exception for analysis errors"""
    pass


class AnalysisTimeoutError(AnalysisError):
    """Raised when analysis times out"""
    pass


class AnalysisFailureError(AnalysisError):
    """Raised when analysis fails unexpectedly"""
    pass


class ServiceUnavailableError(AnalysisError):
    """Raised when external service is unavailable"""
    pass


class ConfigurationError(AnalysisError):
    """Raised when configuration is invalid"""
    pass


@dataclass
class ErrorRecord:
    """Individual error record"""
    timestamp: float
    error_type: str
    error_message: str
    severity: ErrorSeverity
    service: Optional[str] = None
    session_id: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    context: Optional[Dict[str, Any]] = None


class ErrorMetrics:
    """Comprehensive error tracking and analysis"""
    
    def __init__(self, max_history: int = 1000, history_window: int = 3600):
        self.max_history = max_history
        self.history_window = history_window  # seconds
        
        # Error storage
        self.error_history = deque(maxlen=max_history)
        self.error_counts = defaultdict(int)
        self.service_errors = defaultdict(list)
        
        # Recovery tracking
        self.recovery_attempts = 0
        self.successful_recoveries = 0
        self.last_recovery_time = 0
        
        # Performance tracking
        self.response_times = deque(maxlen=100)
        self.fallback_usage = 0
        self.service_downtimes = defaultdict(list)
        
        # Health status
        self.last_health_check = 0
        self._current_health = "unknown"
    
    def record_error(self, error: Exception, 
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    service: Optional[str] = None,
                    session_id: Optional[str] = None,
                    context: Optional[Dict[str, Any]] = None):
        """Record an error occurrence"""
        error_record = ErrorRecord(
            timestamp=time.time(),
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            service=service,
            session_id=session_id,
            context=context or {}
        )
        
        self.error_history.append(error_record)
        self.error_counts[error_record.error_type] += 1
        
        if service:
            self.service_errors[service].append(error_record)
            # Keep only recent service errors
            cutoff = time.time() - self.history_window
            self.service_errors[service] = [
                e for e in self.service_errors[service]
                if e.timestamp > cutoff
            ]
    
    def record_recovery_attempt(self, service: str, successful: bool = False):
        """Record a recovery attempt"""
        self.recovery_attempts += 1
        self.last_recovery_time = time.time()
        
        if successful:
            self.successful_recoveries += 1
            
        # Update recent error records
        for error_record in reversed(self.error_history):
            if (error_record.service == service and 
                not error_record.recovery_attempted and
                time.time() - error_record.timestamp < 300):  # 5 minutes
                error_record.recovery_attempted = True
                error_record.recovery_successful = successful
                break
    
    def record_response_time(self, response_time: float):
        """Record response time for performance tracking"""
        self.response_times.append(response_time)
    
    def record_fallback_usage(self):
        """Record when fallback analyzer is used"""
        self.fallback_usage += 1
    
    def record_service_downtime(self, service: str, start_time: float, end_time: float):
        """Record service downtime period"""
        self.service_downtimes[service].append({
            'start': start_time,
            'end': end_time,
            'duration': end_time - start_time
        })
        
        # Keep only recent downtimes
        cutoff = time.time() - (24 * 3600)  # 24 hours
        self.service_downtimes[service] = [
            d for d in self.service_downtimes[service]
            if d['start'] > cutoff
        ]
    
    def get_recent_errors(self, window_seconds: int = 3600) -> List[ErrorRecord]:
        """Get errors within specified time window"""
        cutoff = time.time() - window_seconds
        return [e for e in self.error_history if e.timestamp > cutoff]
    
    def get_error_rate(self, window_seconds: int = 3600) -> float:
        """Calculate error rate (errors per minute)"""
        recent_errors = len(self.get_recent_errors(window_seconds))
        window_minutes = window_seconds / 60
        return recent_errors / window_minutes if window_minutes > 0 else 0
    
    def get_service_health(self, service: str) -> Dict[str, Any]:
        """Get health metrics for specific service"""
        recent_errors = [
            e for e in self.service_errors[service]
            if time.time() - e.timestamp < 3600
        ]
        
        error_rate = len(recent_errors) / 60  # per minute
        
        # Calculate downtime
        recent_downtimes = [
            d for d in self.service_downtimes[service]
            if time.time() - d['start'] < 24 * 3600
        ]
        total_downtime = sum(d['duration'] for d in recent_downtimes)
        uptime_percentage = max(0, 100 - (total_downtime / (24 * 3600) * 100))
        
        # Determine health status
        if error_rate == 0 and uptime_percentage > 99:
            health_status = "healthy"
        elif error_rate < 0.1 and uptime_percentage > 95:
            health_status = "degraded" 
        elif error_rate < 0.5 and uptime_percentage > 80:
            health_status = "unhealthy"
        else:
            health_status = "critical"
        
        return {
            "service": service,
            "health_status": health_status,
            "error_rate": error_rate,
            "recent_errors": len(recent_errors),
            "uptime_percentage": uptime_percentage,
            "total_downtime_24h": total_downtime,
            "last_error": recent_errors[-1].timestamp if recent_errors else None
        }
    
    def get_overall_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        recent_errors = self.get_recent_errors(3600)
        error_rate = self.get_error_rate(3600)
        
        # Calculate average response time
        avg_response_time = (
            sum(self.response_times) / len(self.response_times) 
            if self.response_times else 0
        )
        
        # Determine overall health
        if error_rate == 0:
            health_status = "healthy"
        elif error_rate < 0.1:
            health_status = "degraded"
        elif error_rate < 0.5:
            health_status = "unhealthy"
        else:
            health_status = "critical"
        
        # Recovery success rate
        recovery_rate = (
            self.successful_recoveries / self.recovery_attempts
            if self.recovery_attempts > 0 else 1.0
        )
        
        self._current_health = health_status
        self.last_health_check = time.time()
        
        return {
            "overall_health": health_status,
            "error_rate_per_minute": error_rate,
            "recent_errors_1h": len(recent_errors),
            "average_response_time": avg_response_time,
            "fallback_usage_count": self.fallback_usage,
            "recovery_success_rate": recovery_rate,
            "recovery_attempts": self.recovery_attempts,
            "successful_recoveries": self.successful_recoveries,
            "last_health_check": self.last_health_check
        }
    
    def should_trigger_recovery(self, service: str) -> bool:
        """Determine if automatic recovery should be attempted"""
        recent_errors = [
            e for e in self.service_errors[service]
            if time.time() - e.timestamp < 300  # 5 minutes
        ]
        
        # Don't retry too frequently
        if time.time() - self.last_recovery_time < 60:
            return False
        
        # Trigger recovery if multiple recent errors
        return len(recent_errors) >= 3
    
    def get_error_trends(self) -> Dict[str, Any]:
        """Analyze error trends and patterns"""
        now = time.time()
        hour_ago = now - 3600
        day_ago = now - 86400
        
        errors_last_hour = len([e for e in self.error_history if e.timestamp > hour_ago])
        errors_last_day = len([e for e in self.error_history if e.timestamp > day_ago])
        
        # Most common errors
        recent_errors = [e for e in self.error_history if e.timestamp > hour_ago]
        error_types = defaultdict(int)
        for error in recent_errors:
            error_types[error.error_type] += 1
        
        top_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Service reliability
        service_reliability = {}
        for service in self.service_errors.keys():
            health = self.get_service_health(service)
            service_reliability[service] = health['uptime_percentage']
        
        return {
            "errors_last_hour": errors_last_hour,
            "errors_last_day": errors_last_day,
            "trend": "increasing" if errors_last_hour > errors_last_day / 24 else "stable",
            "top_error_types": top_errors,
            "service_reliability": service_reliability,
            "analysis_timestamp": now
        }
    
    def export_metrics(self, file_path: Optional[Path] = None) -> Dict[str, Any]:
        """Export all metrics to JSON"""
        if file_path is None:
            file_path = Path.home() / ".claude" / "hooks" / "error_metrics.json"
        
        # Convert error records to dict format
        error_records = [asdict(error) for error in self.error_history]
        
        metrics_data = {
            "export_timestamp": time.time(),
            "error_history": error_records,
            "error_counts": dict(self.error_counts),
            "recovery_stats": {
                "attempts": self.recovery_attempts,
                "successful": self.successful_recoveries,
                "last_attempt": self.last_recovery_time
            },
            "performance_stats": {
                "avg_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0,
                "fallback_usage": self.fallback_usage
            },
            "health_summary": self.get_overall_health(),
            "trends": self.get_error_trends()
        }
        
        # Save to file
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(metrics_data, f, indent=2)
        except Exception as e:
            # Record the export error but don't fail
            self.record_error(e, ErrorSeverity.LOW, context={"operation": "export_metrics"})
        
        return metrics_data
    
    def import_metrics(self, file_path: Path):
        """Import metrics from JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Restore error history
            for error_data in data.get("error_history", []):
                error_record = ErrorRecord(**error_data)
                self.error_history.append(error_record)
            
            # Restore counts
            self.error_counts.update(data.get("error_counts", {}))
            
            # Restore recovery stats
            recovery_stats = data.get("recovery_stats", {})
            self.recovery_attempts = recovery_stats.get("attempts", 0)
            self.successful_recoveries = recovery_stats.get("successful", 0)
            self.last_recovery_time = recovery_stats.get("last_attempt", 0)
            
            # Restore performance stats
            perf_stats = data.get("performance_stats", {})
            self.fallback_usage = perf_stats.get("fallback_usage", 0)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to import metrics: {e}")
    
    def reset_metrics(self):
        """Reset all metrics (for testing or manual reset)"""
        self.error_history.clear()
        self.error_counts.clear()
        self.service_errors.clear()
        self.response_times.clear()
        self.service_downtimes.clear()
        
        self.recovery_attempts = 0
        self.successful_recoveries = 0
        self.last_recovery_time = 0
        self.fallback_usage = 0
        self.last_health_check = 0
        self._current_health = "unknown"
    
    @property
    def current_health(self) -> str:
        """Get current health status"""
        # Refresh if stale
        if time.time() - self.last_health_check > 300:  # 5 minutes
            self.get_overall_health()
        return self._current_health