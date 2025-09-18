"""
CLI display system for tracking events
"""
import json
from datetime import datetime
from typing import Dict, Any
from .config import tracking_config, DisplayLevel, TrackingMode, is_tracking_enabled
from .events import BaseEvent, EventType, SessionEvent, FunctionCallEvent, LLMCallEvent, APICallEvent, ErrorEvent

# Color codes for different platforms
class Colors:
    # ANSI color codes that work on most terminals
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'

def colorize(text: str, color: str) -> str:
    """Add color to text if colors are enabled"""
    if not tracking_config.use_colors:
        return text
    
    color_map = {
        'red': Colors.RED,
        'green': Colors.GREEN,
        'yellow': Colors.YELLOW,
        'blue': Colors.BLUE,
        'magenta': Colors.MAGENTA,
        'cyan': Colors.CYAN,
        'white': Colors.WHITE
    }
    
    color_code = color_map.get(color.lower(), Colors.RESET)
    return f"{color_code}{text}{Colors.RESET}"

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    if tracking_config.show_timestamps:
        return f"[{timestamp.strftime('%H:%M:%S')}] "
    return ""

def format_execution_time(time_ms: float) -> str:
    """Format execution time for display"""
    if not tracking_config.show_execution_time or time_ms is None:
        return ""
    return f" ({time_ms:.1f}ms)"

def display_session_event(event: SessionEvent):
    """Display session start/end events"""
    timestamp = format_timestamp(event.timestamp)
    
    if event.event_type == EventType.SESSION_START:
        message = f"{timestamp}🚀 Session Started"
        if tracking_config.display_level == DisplayLevel.VERBOSE:
            message += f" | ID: {event.session_id[:8]}"
        print(colorize(message, tracking_config.session_color))
        
    elif event.event_type == EventType.SESSION_END:
        message = f"{timestamp}🏁 Session Ended"
        print(colorize(message, tracking_config.session_color))

def display_function_event(event: FunctionCallEvent):
    """Display function call events"""
    if tracking_config.display_level == DisplayLevel.QUIET:
        return
        
    timestamp = format_timestamp(event.timestamp)
    exec_time = format_execution_time(event.execution_time_ms)
    
    # Success/failure indicator
    status = "✅" if event.success else "❌"
    
    message = f"{timestamp}{status} {event.function_name}(){exec_time}"
    
    # Add parameters if enabled and verbose mode
    if (tracking_config.show_parameters and 
        tracking_config.display_level == DisplayLevel.VERBOSE and 
        event.parameters):
        params_str = ", ".join([f"{k}={repr(v)[:50]}" for k, v in event.parameters.items()])
        message += f" | Params: {params_str}"
    
    # Add error message if failed
    if not event.success and event.error_message:
        message += f" | Error: {event.error_message}"
    
    color = tracking_config.function_color if event.success else tracking_config.error_color
    print(colorize(message, color))

def display_llm_event(event: LLMCallEvent):
    """Display LLM call events"""
    if tracking_config.display_level == DisplayLevel.QUIET:
        return
        
    timestamp = format_timestamp(event.timestamp)
    exec_time = format_execution_time(event.response_time_ms)
    
    status = "🤖" if event.success else "❌"
    
    message = f"{timestamp}{status} LLM Call ({event.model_name}){exec_time}"
    
    # Add token and cost info
    if event.tokens_used:
        message += f" | Tokens: {event.tokens_used}"
    if event.estimated_cost:
        message += f" | Cost: ${event.estimated_cost:.4f}"
    
    # Add user input in verbose mode
    if (tracking_config.display_level == DisplayLevel.VERBOSE and 
        event.user_input):
        user_input_preview = event.user_input[:100] + "..." if len(event.user_input) > 100 else event.user_input
        message += f" | Input: '{user_input_preview}'"
    
    # Add error message if failed
    if not event.success and event.error_message:
        message += f" | Error: {event.error_message}"
    
    color = tracking_config.llm_color if event.success else tracking_config.error_color
    print(colorize(message, color))

def display_api_event(event: APICallEvent):
    """Display API call events"""
    if tracking_config.display_level == DisplayLevel.QUIET:
        return
        
    timestamp = format_timestamp(event.timestamp)
    exec_time = format_execution_time(event.response_time_ms)
    
    status = "🌐" if event.success else "❌"
    
    message = f"{timestamp}{status} API Call ({event.api_name}){exec_time}"
    
    # Add status code and method
    if event.status_code:
        message += f" | {event.method} {event.status_code}"
    
    # Add endpoint in verbose mode
    if (tracking_config.display_level == DisplayLevel.VERBOSE and 
        event.endpoint):
        message += f" | {event.endpoint}"
    
    # Add error message if failed
    if not event.success and event.error_message:
        message += f" | Error: {event.error_message}"
    
    color = tracking_config.api_color if event.success else tracking_config.error_color
    print(colorize(message, color))

def display_error_event(event: ErrorEvent):
    """Display error events"""
    timestamp = format_timestamp(event.timestamp)
    
    message = f"{timestamp}💥 ERROR: {event.error_type}"
    if event.function_name:
        message += f" in {event.function_name}()"
    message += f" | {event.error_message}"
    
    print(colorize(message, tracking_config.error_color))
    
    # Show stack trace in verbose mode
    if (tracking_config.display_level == DisplayLevel.VERBOSE and 
        event.stack_trace):
        print(colorize(f"Stack trace: {event.stack_trace}", tracking_config.error_color))

def display_event(event: BaseEvent):
    """Main function to display any tracking event"""
    if not is_tracking_enabled() or tracking_config.mode != TrackingMode.CLI:
        return
    
    if isinstance(event, SessionEvent):
        display_session_event(event)
    elif isinstance(event, FunctionCallEvent):
        display_function_event(event)
    elif isinstance(event, LLMCallEvent):
        display_llm_event(event)
    elif isinstance(event, APICallEvent):
        display_api_event(event)
    elif isinstance(event, ErrorEvent):
        display_error_event(event)

def display_session_summary(summary: Dict[str, Any]):
    """Display session summary at the end"""
    if not is_tracking_enabled() or tracking_config.mode != TrackingMode.CLI:
        return
        
    print("\n" + "="*50)
    print(colorize("📊 SESSION SUMMARY", tracking_config.session_color))
    print("="*50)
    
    if summary.get('total_time_seconds'):
        print(f"⏱️  Duration: {summary['total_time_seconds']:.1f} seconds")
    
    print(f"🔧 Function calls: {summary.get('function_calls_count', 0)}")
    print(f"🤖 LLM calls: {summary.get('llm_calls_count', 0)}")
    print(f"🌐 API calls: {summary.get('api_calls_count', 0)}")
    
    if summary.get('errors_count', 0) > 0:
        print(colorize(f"💥 Errors: {summary['errors_count']}", tracking_config.error_color))
    
    if summary.get('total_estimated_cost', 0) > 0:
        cost_color = tracking_config.error_color if summary['total_estimated_cost'] > 0.10 else tracking_config.function_color
        print(colorize(f"💰 Total estimated cost: ${summary['total_estimated_cost']:.4f}", cost_color))
    
    print("="*50 + "\n") 