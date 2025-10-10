"""
Decorators for tracking agent functions, LLM calls, and API calls.
"""
import time
import functools
from typing import Callable, Any

from .events import emit_event, FunctionCallEvent, LLMCallEvent, APICallEvent, ErrorEvent, EventType
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

def track_llm(func: Callable) -> Callable:
    """
    A decorator specifically for tracking LLM API calls.

    It assumes the wrapped function takes a `prompt` string and returns
    a response object that has a `.text` attribute and potentially
    token usage information.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not is_tracking_enabled():
            return func(*args, **kwargs)

        # Extract model and prompt from arguments
        # Assumes 'model' is a keyword argument or the second positional argument
        # Assumes 'prompt' is a keyword argument or the third positional argument
        prompt = kwargs.get('prompt', args[2] if len(args) > 2 else None)
        model_obj = kwargs.get('model', args[1] if len(args) > 1 else None)
        model_name = getattr(model_obj, 'model_name', 'unknown_model') if model_obj else 'unknown_model'
        user_input = kwargs.get('user_input', None)

        start_time = time.perf_counter()
        error = None
        response = None

        try:
            response = func(*args, **kwargs)
            return response
        except Exception as e:
            error = e
            raise
        finally:
            end_time = time.perf_counter()
            response_time_ms = (end_time - start_time) * 1000

            # Estimate token usage and cost (simplified)
            # A more accurate method would use the API response's usage metadata
            llm_response_text = getattr(response, 'text', '') if response else ''
            prompt_tokens = len(prompt.split()) if prompt else 0
            response_tokens = len(llm_response_text.split())
            total_tokens = prompt_tokens + response_tokens

            # Simplified cost for Gemini Flash model: ~$0.0001 per 1K tokens
            estimated_cost = (total_tokens / 1000) * 0.0001

            event = LLMCallEvent(
                event_type=EventType.LLM_CALL,
                model_name=model_name.split('/')[-1], # Clean up model name
                prompt_length=len(prompt) if prompt else 0,
                response_length=len(llm_response_text),
                tokens_used=total_tokens,
                estimated_cost=estimated_cost,
                response_time_ms=response_time_ms,
                success=error is None,
                user_input=user_input,
                llm_response=llm_response_text,
                error_message=str(error) if error else None
            )
            emit_event(event)

    return wrapper
