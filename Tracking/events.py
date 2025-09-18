"""
Event data structures for tracking
"""
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum

class EventType(Enum):
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    FUNCTION_CALL = "function_call"
    LLM_CALL = "llm_call"
    API_CALL = "api_call"
    ERROR = "error"

@dataclass
class BaseEvent:
    """Base event structure"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    event_type: EventType = EventType.FUNCTION_CALL

@dataclass
class SessionEvent(BaseEvent):
    """Session start/end events"""
    user_id: Optional[str] = None
    agent_version: Optional[str] = None
    
@dataclass
class FunctionCallEvent(BaseEvent):
    """Function call tracking event"""
    function_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    success: bool = True
    return_value: Any = None
    error_message: Optional[str] = None
    
@dataclass
class LLMCallEvent(BaseEvent):
    """LLM call tracking event"""
    model_name: str = ""
    prompt_length: int = 0
    response_length: int = 0
    tokens_used: Optional[int] = None
    estimated_cost: Optional[float] = None
    response_time_ms: Optional[float] = None
    success: bool = True
    user_input: Optional[str] = None
    llm_response: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class APICallEvent(BaseEvent):
    """API call tracking event"""
    api_name: str = ""
    endpoint: str = ""
    method: str = "GET"
    response_time_ms: Optional[float] = None
    status_code: Optional[int] = None
    success: bool = True
    request_size: Optional[int] = None
    response_size: Optional[int] = None
    error_message: Optional[str] = None

@dataclass
class ErrorEvent(BaseEvent):
    """Error tracking event"""
    error_type: str = ""
    error_message: str = ""
    stack_trace: Optional[str] = None
    function_name: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

# Global session tracking
current_session_id: str = ""
session_events: List[BaseEvent] = []

def start_session(user_id: Optional[str] = None) -> str:
    """Start a new tracking session"""
    global current_session_id, session_events
    current_session_id = str(uuid.uuid4())
    session_events = []
    
    event = SessionEvent(
        session_id=current_session_id,
        event_type=EventType.SESSION_START,
        user_id=user_id
    )
    session_events.append(event)
    return current_session_id

def end_session() -> str:
    """End the current tracking session"""
    global current_session_id, session_events
    
    event = SessionEvent(
        session_id=current_session_id,
        event_type=EventType.SESSION_END
    )
    session_events.append(event)
    
    ended_session = current_session_id
    current_session_id = ""
    return ended_session

def emit_event(event: BaseEvent):
    """Emit a tracking event"""
    global current_session_id, session_events
    
    if not current_session_id:
        # Auto-start session if not started
        start_session()
    
    event.session_id = current_session_id
    session_events.append(event)
    
    # Import here to avoid circular imports
    from .display import display_event
    display_event(event)

def get_session_events() -> List[BaseEvent]:
    """Get all events for the current session"""
    return session_events.copy()

def get_session_summary() -> Dict[str, Any]:
    """Get a summary of the current session"""
    if not session_events:
        return {}
    
    function_calls = [e for e in session_events if e.event_type == EventType.FUNCTION_CALL]
    llm_calls = [e for e in session_events if e.event_type == EventType.LLM_CALL]
    api_calls = [e for e in session_events if e.event_type == EventType.API_CALL]
    errors = [e for e in session_events if e.event_type == EventType.ERROR]
    
    session_start = next((e for e in session_events if e.event_type == EventType.SESSION_START), None)
    session_end = next((e for e in session_events if e.event_type == EventType.SESSION_END), None)
    
    total_time = None
    if session_start and session_end:
        total_time = (session_end.timestamp - session_start.timestamp).total_seconds()
    
    total_cost = sum(e.estimated_cost or 0 for e in llm_calls)
    
    return {
        "session_id": current_session_id,
        "total_time_seconds": total_time,
        "function_calls_count": len(function_calls),
        "llm_calls_count": len(llm_calls),
        "api_calls_count": len(api_calls),
        "errors_count": len(errors),
        "total_estimated_cost": total_cost,
        "session_start": session_start.timestamp if session_start else None,
        "session_end": session_end.timestamp if session_end else None
    }
