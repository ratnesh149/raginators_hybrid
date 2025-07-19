# Configuration Settings for HR Assistant
# Custom implementation settings

import os
from typing import Dict, Any

class HRAssistantConfig:
    """Configuration management for HR Assistant system"""
    
    # System settings
    DEFAULT_THREAD_PREFIX = "hr_session"
    MAX_CONVERSATION_TURNS = 50
    ENABLE_DEBUG_MODE = False
    
    # Agent configuration
    AGENT_NAMES = {
        "chatbot": "Conversation Manager",
        "jd_agent": "Job Description Specialist", 
        "checklist_agent": "Hiring Process Coordinator"
    }
    
    # Display settings
    RESPONSE_SEPARATOR = "=" * 50
    AGENT_SEPARATOR = "-" * 40
    
    @classmethod
    def get_session_config(cls, session_id: str = None) -> Dict[str, Any]:
        """Generate session configuration"""
        if not session_id:
            session_id = f"{cls.DEFAULT_THREAD_PREFIX}_001"
            
        return {
            "configurable": {
                "thread_id": session_id,
                "max_turns": cls.MAX_CONVERSATION_TURNS
            },
            "recursion_limit": 50  # Increase recursion limit to handle complex conversations
        }
    
    @classmethod
    def get_agent_display_name(cls, agent_key: str) -> str:
        """Get formatted agent display name"""
        return cls.AGENT_NAMES.get(agent_key, agent_key.title())
