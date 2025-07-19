# Utility Functions for HR Assistant
# Common helper functions and formatting utilities

import datetime
import json
from typing import Any, List, Dict, Union

class MessageFormatter:
    """Handles message formatting and display"""
    
    @staticmethod
    def format_agent_response(agent_name: str, content: Any) -> str:
        """Format agent response for display"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_name = agent_name.replace('_', ' ').title()
        
        return f"[{timestamp}] 🤖 {formatted_name}: {content}"
    
    @staticmethod
    def format_user_input(content: str) -> str:
        """Format user input for display"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] 👤 User: {content}"

class SessionManager:
    """Manages session state and metadata"""
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate unique session identifier"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"hr_session_{timestamp}"
    
    @staticmethod
    def log_session_event(event_type: str, details: Dict[str, Any]) -> None:
        """Log session events for debugging"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        # In a real implementation, this would write to a log file
        print(f"[DEBUG] {json.dumps(log_entry, indent=2)}")

class ValidationHelper:
    """Input validation and sanitization"""
    
    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Basic input sanitization"""
        return user_input.strip()[:1000]  # Limit length
    
    @staticmethod
    def validate_agent_name(agent_name: str) -> bool:
        """Validate agent name"""
        valid_agents = ["chatbot", "jd_agent", "checklist_agent"]
        return agent_name in valid_agents
