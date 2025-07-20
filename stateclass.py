"""
State class for the HR Assistant application
Defines the state structure used throughout the LangGraph workflow
"""

from typing_extensions import TypedDict
from typing import List, Any, Optional
from langchain_core.messages import BaseMessage

class State(TypedDict):
    """
    State class for the HR Assistant workflow
    
    Contains:
    - messages: List of conversation messages
    - next: Next node to route to
    - Any additional state data needed by agents
    """
    messages: List[BaseMessage]
    next: Optional[str]
    # Additional fields can be added as needed by agents
