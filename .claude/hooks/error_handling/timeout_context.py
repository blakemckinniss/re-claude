"""
Timeout context manager for preventing hanging operations
"""

import signal
import time
from contextlib import contextmanager
from typing import Optional, Any


class TimeoutError(Exception):
    """Raised when operation times out"""
    pass


@contextmanager
def timeout_context(seconds: int, error_message: Optional[str] = None):
    """
    Context manager that raises TimeoutError if operation takes too long
    
    Args:
        seconds: Maximum time to allow operation
        error_message: Custom error message
    
    Usage:
        with timeout_context(30):
            # Operation that might hang
            result = slow_operation()
    """
    if error_message is None:
        error_message = f"Operation timed out after {seconds} seconds"
    
    def timeout_handler(signum, frame):
        raise TimeoutError(error_message)
    
    # Set up the timeout
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Cancel the alarm and restore old handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


class OperationTimer:
    """Timer for measuring operation duration with timeout support"""
    
    def __init__(self, name: str, timeout: Optional[int] = None):
        self.name = name
        self.timeout = timeout
        self.start_time = None
        self.end_time = None
        self.timed_out = False
    
    def __enter__(self):
        self.start_time = time.time()
        if self.timeout:
            def timeout_handler(signum, frame):
                self.timed_out = True
                raise TimeoutError(f"{self.name} timed out after {self.timeout} seconds")
            
            self.old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        
        if self.timeout:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, self.old_handler)
        
        # Don't suppress timeout exceptions
        if exc_type is TimeoutError:
            self.timed_out = True
            return False
    
    @property
    def duration(self) -> float:
        """Get operation duration in seconds"""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time
    
    @property
    def duration_ms(self) -> int:
        """Get operation duration in milliseconds"""
        return int(self.duration * 1000)


class AdaptiveTimeout:
    """Adaptive timeout that adjusts based on historical performance"""
    
    def __init__(self, base_timeout: int = 30, max_timeout: int = 120):
        self.base_timeout = base_timeout
        self.max_timeout = max_timeout
        self.history = []
        self.max_history = 10
    
    def get_timeout(self) -> int:
        """Get recommended timeout based on history"""
        if not self.history:
            return self.base_timeout
        
        # Calculate average with some buffer
        avg_duration = sum(self.history) / len(self.history)
        recommended = int(avg_duration * 2.5)  # 2.5x buffer
        
        return min(max(recommended, self.base_timeout), self.max_timeout)
    
    def record_duration(self, duration: float):
        """Record successful operation duration"""
        self.history.append(duration)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    @contextmanager
    def adaptive_timeout_context(self, operation_name: str = "operation"):
        """Context manager with adaptive timeout"""
        timeout_seconds = self.get_timeout()
        
        with OperationTimer(operation_name, timeout_seconds) as timer:
            try:
                yield timer
                if not timer.timed_out:
                    self.record_duration(timer.duration)
            except TimeoutError:
                # Don't record timeout durations
                raise


class RetryWithTimeout:
    """Retry mechanism with timeout and exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def execute(self, func, timeout: int, *args, **kwargs) -> Any:
        """Execute function with retries and timeout"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                with timeout_context(timeout):
                    return func(*args, **kwargs)
            except TimeoutError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    time.sleep(delay)
                continue
            except Exception as e:
                # For non-timeout errors, don't retry
                raise e
        
        # All retries exhausted
        raise last_exception


# Convenient decorators
def with_timeout(seconds: int):
    """Decorator to add timeout to function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with timeout_context(seconds):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def with_adaptive_timeout(base_timeout: int = 30, max_timeout: int = 120):
    """Decorator to add adaptive timeout to function"""
    adaptive = AdaptiveTimeout(base_timeout, max_timeout)
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            with adaptive.adaptive_timeout_context(func.__name__) as timer:
                return func(*args, **kwargs)
        return wrapper
    return decorator


def with_retry_timeout(max_retries: int = 3, timeout: int = 30, base_delay: float = 1.0):
    """Decorator to add retry with timeout to function"""
    retry_handler = RetryWithTimeout(max_retries, base_delay)
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            return retry_handler.execute(func, timeout, *args, **kwargs)
        return wrapper
    return decorator