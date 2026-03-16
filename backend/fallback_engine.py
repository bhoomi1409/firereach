"""
Circuit Breaker Pattern for API Fallbacks
Tracks failures per service. After 3 failures → OPEN (skip for 60s).
"""

import time
from typing import Any, Callable, Optional
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"    # Normal operation
    OPEN   = "open"      # Skip calls, return None
    HALF_OPEN = "half_open"  # Test if service recovered

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 3, timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitState.CLOSED

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        else:  # HALF_OPEN
            return True

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Global circuit breakers
CIRCUITS = {
    # Contact enrichment
    "hunter_domain":  CircuitBreaker("hunter_domain"),
    "hunter_finder":  CircuitBreaker("hunter_finder"),
    "hunter_verify":  CircuitBreaker("hunter_verify"),
    
    # Signal sources
    "newsapi":        CircuitBreaker("newsapi"),
    "serper":         CircuitBreaker("serper"),
    "groq":           CircuitBreaker("groq"),
}

async def try_with_circuit(
    circuit_name: str,
    func: Callable,
    *args,
    **kwargs
) -> Optional[Any]:
    """
    Execute function with circuit breaker protection.
    Returns None if circuit is OPEN or function fails.
    """
    circuit = CIRCUITS.get(circuit_name)
    if not circuit or not circuit.can_execute():
        return None

    try:
        result = await func(*args, **kwargs)
        circuit.record_success()
        return result
    except Exception:
        circuit.record_failure()
        return None