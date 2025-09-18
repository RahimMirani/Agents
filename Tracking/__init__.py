"""
Tracking module for agent monitoring and analytics
"""

from .config import (
    TrackingMode, 
    DisplayLevel, 
    TrackingConfig, 
    tracking_config,
    set_tracking_mode,
    set_display_level,
    is_tracking_enabled
)

from .events import (
    EventType,
    BaseEvent,
    SessionEvent,
    FunctionCallEvent,
    LLMCallEvent,
    APICallEvent,
    ErrorEvent,
    start_session,
    end_session,
    emit_event,
    get_session_events,
    get_session_summary
)

__version__ = "0.1.0"
__author__ = "Agent Developer"

# Make key functions easily accessible
__all__ = [
    # Config
    "TrackingMode", "DisplayLevel", "tracking_config",
    "set_tracking_mode", "set_display_level", "is_tracking_enabled",
    
    # Events
    "EventType", "start_session", "end_session", "emit_event",
    "get_session_events", "get_session_summary",
    
    # Event types
    "BaseEvent", "SessionEvent", "FunctionCallEvent", 
    "LLMCallEvent", "APICallEvent", "ErrorEvent"
] 