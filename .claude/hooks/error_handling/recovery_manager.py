"""
Recovery manager for automatic service restoration and health monitoring
"""

import time
import json
import asyncio
import threading
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict

from .error_metrics import ErrorMetrics, ErrorSeverity
from .circuit_breaker import MultiServiceCircuitBreaker


class RecoveryStrategy(Enum):
    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"
    MAINTENANCE = "maintenance"


@dataclass
class ServiceConfig:
    """Configuration for a monitored service"""
    name: str
    health_check: Callable[[], bool]
    recovery_action: Callable[[], bool]
    strategy: RecoveryStrategy = RecoveryStrategy.EXPONENTIAL_BACKOFF
    max_retries: int = 3
    base_delay: float = 60.0  # seconds
    max_delay: float = 900.0  # 15 minutes
    health_check_interval: int = 300  # 5 minutes
    enabled: bool = True


class ServiceHealthChecker:
    """Health checker for individual services"""
    
    def __init__(self, service_config: ServiceConfig, error_metrics: ErrorMetrics):
        self.config = service_config
        self.error_metrics = error_metrics
        self.status = ServiceStatus.HEALTHY
        self.last_check = 0
        self.last_failure = 0
        self.retry_count = 0
        self.next_retry = 0
        
    def check_health(self) -> bool:
        """Check if service is healthy"""
        if not self.config.enabled:
            return True
            
        try:
            self.last_check = time.time()
            healthy = self.config.health_check()
            
            if healthy:
                if self.status in [ServiceStatus.FAILED, ServiceStatus.RECOVERING]:
                    self._on_recovery()
                else:
                    self.status = ServiceStatus.HEALTHY
                return True
            else:
                self._on_failure()
                return False
                
        except Exception as e:
            self.error_metrics.record_error(
                e, ErrorSeverity.HIGH, self.config.name,
                context={"operation": "health_check"}
            )
            self._on_failure()
            return False
    
    def attempt_recovery(self) -> bool:
        """Attempt to recover the service"""
        if not self._should_retry():
            return False
            
        try:
            self.status = ServiceStatus.RECOVERING
            self.retry_count += 1
            
            success = self.config.recovery_action()
            
            if success:
                self._on_recovery()
                self.error_metrics.record_recovery_attempt(self.config.name, True)
                return True
            else:
                self._schedule_next_retry()
                self.error_metrics.record_recovery_attempt(self.config.name, False)
                return False
                
        except Exception as e:
            self.error_metrics.record_error(
                e, ErrorSeverity.HIGH, self.config.name,
                context={"operation": "recovery_attempt"}
            )
            self._schedule_next_retry()
            self.error_metrics.record_recovery_attempt(self.config.name, False)
            return False
    
    def _on_failure(self):
        """Handle service failure"""
        self.last_failure = time.time()
        self.status = ServiceStatus.FAILED
        if self.retry_count == 0:  # First failure
            self._schedule_next_retry()
    
    def _on_recovery(self):
        """Handle service recovery"""
        self.status = ServiceStatus.HEALTHY
        self.retry_count = 0
        self.next_retry = 0
    
    def _should_retry(self) -> bool:
        """Check if we should attempt recovery"""
        if self.retry_count >= self.config.max_retries:
            return False
        if time.time() < self.next_retry:
            return False
        return True
    
    def _schedule_next_retry(self):
        """Schedule next recovery attempt"""
        if self.config.strategy == RecoveryStrategy.IMMEDIATE:
            delay = 0
        elif self.config.strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
            delay = min(
                self.config.base_delay * (2 ** self.retry_count),
                self.config.max_delay
            )
        else:
            delay = self.config.base_delay
            
        self.next_retry = time.time() + delay
    
    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return {
            "name": self.config.name,
            "status": self.status.value,
            "last_check": self.last_check,
            "last_failure": self.last_failure,
            "retry_count": self.retry_count,
            "next_retry": self.next_retry,
            "enabled": self.config.enabled
        }


class RecoveryManager:
    """Manages automatic recovery for multiple services"""
    
    def __init__(self, error_metrics: ErrorMetrics, circuit_breaker: MultiServiceCircuitBreaker):
        self.error_metrics = error_metrics
        self.circuit_breaker = circuit_breaker
        self.services: Dict[str, ServiceHealthChecker] = {}
        self.monitoring_enabled = False
        self.monitor_thread = None
        self.stop_monitoring = threading.Event()
        
        # Recovery state
        self.recovery_history = []
        self.maintenance_mode = False
        self.auto_recovery_enabled = True
        
        # Configuration
        self.global_check_interval = 60  # seconds
        self.max_concurrent_recoveries = 2
        self.active_recoveries = set()
    
    def register_service(self, service_config: ServiceConfig):
        """Register a service for monitoring and recovery"""
        checker = ServiceHealthChecker(service_config, self.error_metrics)
        self.services[service_config.name] = checker
    
    def unregister_service(self, service_name: str):
        """Unregister a service"""
        if service_name in self.services:
            del self.services[service_name]
    
    def enable_service(self, service_name: str):
        """Enable monitoring for a service"""
        if service_name in self.services:
            self.services[service_name].config.enabled = True
    
    def disable_service(self, service_name: str):
        """Disable monitoring for a service"""
        if service_name in self.services:
            self.services[service_name].config.enabled = False
    
    def start_monitoring(self):
        """Start background monitoring and recovery"""
        if self.monitoring_enabled:
            return
            
        self.monitoring_enabled = True
        self.stop_monitoring.clear()
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if not self.monitoring_enabled:
            return
            
        self.monitoring_enabled = False
        self.stop_monitoring.set()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_monitoring.wait(self.global_check_interval):
            if self.maintenance_mode:
                continue
                
            try:
                self._check_all_services()
                self._attempt_recoveries()
                self._cleanup_history()
            except Exception as e:
                self.error_metrics.record_error(
                    e, ErrorSeverity.MEDIUM,
                    context={"operation": "monitoring_loop"}
                )
    
    def _check_all_services(self):
        """Check health of all registered services"""
        for service_name, checker in self.services.items():
            if not checker.config.enabled:
                continue
                
            # Check if it's time for health check
            time_since_check = time.time() - checker.last_check
            if time_since_check >= checker.config.health_check_interval:
                try:
                    healthy = checker.check_health()
                    if not healthy and service_name in self.circuit_breaker.breakers:
                        # Force circuit breaker open for failed services
                        self.circuit_breaker.breakers[service_name].force_open()
                except Exception as e:
                    self.error_metrics.record_error(
                        e, ErrorSeverity.HIGH, service_name,
                        context={"operation": "health_check"}
                    )
    
    def _attempt_recoveries(self):
        """Attempt recovery for failed services"""
        if not self.auto_recovery_enabled:
            return
            
        if len(self.active_recoveries) >= self.max_concurrent_recoveries:
            return
            
        for service_name, checker in self.services.items():
            if (service_name not in self.active_recoveries and
                checker.status == ServiceStatus.FAILED and
                checker._should_retry()):
                
                self.active_recoveries.add(service_name)
                threading.Thread(
                    target=self._perform_recovery,
                    args=(service_name, checker),
                    daemon=True
                ).start()
    
    def _perform_recovery(self, service_name: str, checker: ServiceHealthChecker):
        """Perform recovery for a specific service"""
        try:
            success = checker.attempt_recovery()
            
            # Record recovery attempt
            recovery_record = {
                "timestamp": time.time(),
                "service": service_name,
                "success": success,
                "retry_count": checker.retry_count
            }
            self.recovery_history.append(recovery_record)
            
            if success:
                # Reset circuit breaker
                if service_name in self.circuit_breaker.breakers:
                    self.circuit_breaker.breakers[service_name].reset()
                    
        except Exception as e:
            self.error_metrics.record_error(
                e, ErrorSeverity.HIGH, service_name,
                context={"operation": "recovery_attempt"}
            )
        finally:
            self.active_recoveries.discard(service_name)
    
    def _cleanup_history(self):
        """Clean up old recovery history"""
        cutoff = time.time() - 86400  # 24 hours
        self.recovery_history = [
            r for r in self.recovery_history
            if r["timestamp"] > cutoff
        ]
    
    def manual_recovery(self, service_name: str) -> bool:
        """Manually trigger recovery for a service"""
        if service_name not in self.services:
            return False
            
        checker = self.services[service_name]
        
        # Force a retry even if not scheduled
        old_next_retry = checker.next_retry
        old_retry_count = checker.retry_count
        
        checker.next_retry = 0
        if checker.retry_count >= checker.config.max_retries:
            checker.retry_count = checker.config.max_retries - 1
            
        try:
            return checker.attempt_recovery()
        finally:
            # Restore state if recovery failed
            if checker.status != ServiceStatus.HEALTHY:
                checker.next_retry = old_next_retry
                checker.retry_count = old_retry_count
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        service_statuses = {}
        healthy_count = 0
        
        for service_name, checker in self.services.items():
            status = checker.get_status()
            service_statuses[service_name] = status
            if status["status"] == "healthy":
                healthy_count += 1
        
        # Overall health assessment
        total_services = len(self.services)
        if total_services == 0:
            overall_health = "unknown"
        elif healthy_count == total_services:
            overall_health = "healthy"
        elif healthy_count >= total_services * 0.8:
            overall_health = "degraded"
        else:
            overall_health = "critical"
        
        # Recent recovery stats
        recent_recoveries = [
            r for r in self.recovery_history
            if time.time() - r["timestamp"] < 3600
        ]
        
        successful_recoveries = sum(1 for r in recent_recoveries if r["success"])
        recovery_success_rate = (
            successful_recoveries / len(recent_recoveries)
            if recent_recoveries else 1.0
        )
        
        return {
            "overall_health": overall_health,
            "monitoring_enabled": self.monitoring_enabled,
            "maintenance_mode": self.maintenance_mode,
            "auto_recovery_enabled": self.auto_recovery_enabled,
            "total_services": total_services,
            "healthy_services": healthy_count,
            "active_recoveries": len(self.active_recoveries),
            "recent_recoveries": len(recent_recoveries),
            "recovery_success_rate": recovery_success_rate,
            "services": service_statuses
        }
    
    def enter_maintenance_mode(self):
        """Enter maintenance mode (disable auto-recovery)"""
        self.maintenance_mode = True
        self.auto_recovery_enabled = False
    
    def exit_maintenance_mode(self):
        """Exit maintenance mode (re-enable auto-recovery)"""
        self.maintenance_mode = False
        self.auto_recovery_enabled = True
    
    def export_status(self, file_path: Optional[Path] = None) -> Dict[str, Any]:
        """Export system status to file"""
        if file_path is None:
            file_path = Path.home() / ".claude" / "hooks" / "recovery_status.json"
        
        status_data = self.get_system_status()
        status_data["export_timestamp"] = time.time()
        status_data["recovery_history"] = self.recovery_history[-50:]  # Last 50 records
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            self.error_metrics.record_error(
                e, ErrorSeverity.LOW,
                context={"operation": "export_status"}
            )
        
        return status_data
    
    def get_recovery_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for system recovery"""
        recommendations = []
        
        for service_name, checker in self.services.items():
            if checker.status == ServiceStatus.FAILED:
                if checker.retry_count >= checker.config.max_retries:
                    recommendations.append({
                        "type": "manual_intervention",
                        "service": service_name,
                        "priority": "high",
                        "message": f"Service {service_name} has exhausted auto-recovery attempts. Manual intervention required."
                    })
                elif not checker.config.enabled:
                    recommendations.append({
                        "type": "enable_service",
                        "service": service_name,
                        "priority": "medium",
                        "message": f"Service {service_name} is disabled. Enable to restore functionality."
                    })
        
        # System-wide recommendations
        if self.maintenance_mode:
            recommendations.append({
                "type": "exit_maintenance",
                "service": "system",
                "priority": "medium", 
                "message": "System is in maintenance mode. Exit to enable auto-recovery."
            })
        
        if not self.monitoring_enabled:
            recommendations.append({
                "type": "enable_monitoring",
                "service": "system",
                "priority": "high",
                "message": "Service monitoring is disabled. Enable for automatic health checks."
            })
        
        return recommendations