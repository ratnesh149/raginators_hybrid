# State Management for HR Assistant System
# Defines the shared state structure across all agents

from langgraph.graph import MessagesState, add_messages
from typing_extensions import Annotated
from typing import List, Optional

class State(MessagesState):
    """
    Enhanced state class for HR Assistant workflow management
    
    Attributes:
        next: Next agent/node to execute
        messages: Conversation history with automatic message aggregation
        sender: Current message sender identifier
        roles: List of job roles being processed
        current_role_index: Index of currently active role
        session_metadata: Additional session information
    """
    
    # Core workflow control
    next: str
    messages: Annotated[list, add_messages]
    sender: str
    
    # Role management
    roles: List[str] = []
    current_role_index: int = 0
    
    # Extended functionality
    session_metadata: Optional[dict] = None
    
    def __init__(self, **data):
        """Initialize state with default values"""
        super().__init__(**data)
        if self.session_metadata is None:
            self.session_metadata = {}


