"""
Circuit breaker pattern implementation for analyzer resilience
"""

import time
import functools
from typing import Any, Callable, Optional
from enum import Enum


class CircuitBreakerState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class AnalyzerCircuitBreaker:
    """Circuit breaker for analyzer service calls"""
    
    def __init__(self, 
                 failure_threshold: int = 3,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        # State tracking
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitBreakerState.CLOSED
        
        # Statistics
        self.call_count = 0
        self.success_count = 0
        self.failure_total = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        self.call_count += 1
        
        # Check if circuit is open
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. Failing fast. "
                    f"Last failure: {self.last_failure_time}"
                )
        
        try:
            # Attempt the call
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.success_count += 1
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Recovery successful, close circuit
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.failure_total += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Failed during recovery test, back to open
            self.state = CircuitBreakerState.OPEN
    
    @property
    def is_open(self) -> bool:
        """Check if circuit breaker is open"""
        return self.state == CircuitBreakerState.OPEN
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit breaker is closed"""
        return self.state == CircuitBreakerState.CLOSED
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.call_count == 0:
            return 1.0
        return self.success_count / self.call_count
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "call_count": self.call_count,
            "success_count": self.success_count,
            "failure_total": self.failure_total,
            "success_rate": self.success_rate,
            "last_failure_time": self.last_failure_time,
            "recovery_timeout": self.recovery_timeout
        }
    
    def reset(self):
        """Manually reset circuit breaker"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
    
    def force_open(self):
        """Manually open circuit breaker"""
        self.state = CircuitBreakerState.OPEN
        self.last_failure_time = time.time()


def circuit_breaker(failure_threshold: int = 3, 
                   recovery_timeout: int = 60,
                   expected_exception: type = Exception):
    """Decorator for applying circuit breaker pattern"""
    
    def decorator(func: Callable) -> Callable:
        cb = AnalyzerCircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception
        )
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        
        # Attach circuit breaker to function for external access
        wrapper._circuit_breaker = cb
        return wrapper
    
    return decorator


class MultiServiceCircuitBreaker:
    """Circuit breaker manager for multiple services"""
    
    def __init__(self):
        self.breakers = {}
    
    def get_breaker(self, service_name: str, **kwargs) -> AnalyzerCircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.breakers:
            self.breakers[service_name] = AnalyzerCircuitBreaker(**kwargs)
        return self.breakers[service_name]
    
    def call_service(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """Call service through its circuit breaker"""
        breaker = self.get_breaker(service_name)
        return breaker.call(func, *args, **kwargs)
    
    def get_all_stats(self) -> dict:
        """Get statistics for all services"""
        return {
            service: breaker.get_stats() 
            for service, breaker in self.breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            breaker.reset()
    
    def get_healthy_services(self) -> list:
        """Get list of services with closed circuit breakers"""
        return [
            service for service, breaker in self.breakers.items()
            if breaker.is_closed
        ]
    
    def get_failed_services(self) -> list:
        """Get list of services with open circuit breakers"""
        return [
            service for service, breaker in self.breakers.items()
            if breaker.is_open
        ]