"""
Tracking configuration settings
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class TrackingMode(Enum):
    CLI = "cli"
    FILE = "file"
    WEBHOOK = "webhook"
    DISABLED = "disabled"

class DisplayLevel(Enum):
    QUIET = "quiet"      # Only session start/end and errors
    NORMAL = "normal"    # Function calls and LLM calls
    VERBOSE = "verbose"  # Everything including detailed parameters

@dataclass
class TrackingConfig:
    """Configuration for the tracking system"""
    mode: TrackingMode = TrackingMode.CLI
    display_level: DisplayLevel = DisplayLevel.NORMAL
    show_parameters: bool = True
    show_execution_time: bool = True
    show_timestamps: bool = True
    webhook_url: Optional[str] = None
    log_file_path: Optional[str] = None
    
    # Color settings for CLI
    use_colors: bool = True
    session_color: str = "cyan"
    function_color: str = "green"
    llm_color: str = "blue"
    api_color: str = "yellow"
    error_color: str = "red"

# Global configuration instance
tracking_config = TrackingConfig()

def set_tracking_mode(mode: TrackingMode):
    """Change the tracking mode"""
    global tracking_config
    tracking_config.mode = mode

def set_display_level(level: DisplayLevel):
    """Change the display level"""
    global tracking_config
    tracking_config.display_level = level

def is_tracking_enabled() -> bool:
    """Check if tracking is enabled"""
    return tracking_config.mode != TrackingMode.DISABLED
