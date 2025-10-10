"""
Decorators for tracking agent functions, LLM calls, and API calls.
"""
import time
import functools
from typing import Callable, Any

from .events import emit_event, FunctionCallEvent, LLMCallEvent, APICallEvent, ErrorEvent
from .config import is_tracking_enabled

def track_function(func: Callable) -> Callable:
    """
    A decorator to track the execution of a function.

    Captures:
    - Function name and parameters
    - Execution time
    - Success or failure (exceptions)
    - Return value
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not is_tracking_enabled():
            return func(*args, **kwargs)

        start_time = time.perf_counter()
        error = None
        return_value = None

        try:
            return_value = func(*args, **kwargs)
            return return_value
        except Exception as e:
            error = e
            # Re-raise the exception after tracking
            raise
        finally:
            end_time = time.perf_counter()
            execution_time_ms = (end_time - start_time) * 1000

            # Prepare parameters for serialization
            # Avoids including large objects like 'service'
            params_to_log = {}
            for i, arg in enumerate(args):
                if i > 0: # Skip the 'service' or 'self' object, usually the first arg
                    params_to_log[f"arg_{i}"] = repr(arg)
            for key, value in kwargs.items():
                params_to_log[key] = repr(value)


            event = FunctionCallEvent(
                function_name=func.__name__,
                parameters=params_to_log,
                execution_time_ms=execution_time_ms,
                success=error is None,
                return_value=repr(return_value) if return_value else None,
                error_message=str(error) if error else None
            )
            emit_event(event)

    return wrapper
