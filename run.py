# HR Assistant Application Entry Point
# Author: Custom Implementation
# Version: 1.0

from graph.stategraph import graph
from stateclass import State
from config import HRAssistantConfig
from utils import MessageFormatter, SessionManager, ValidationHelper
import sys
import os

# HR Assistant Application Entry Point
# Author: Custom Implementation
# Version: 1.0

from graph.stategraph import graph
from stateclass import State
from config import HRAssistantConfig
from utils import MessageFormatter, SessionManager, ValidationHelper
from tools.document_processor import initialize_sample_data
import sys
import os

def initialize_hr_system():
    """Initialize the HR assistant system with custom configuration"""
    print("🚀 Advanced HR Management System Starting...")
    print("📊 Initializing Vector Database...")
    
    # Initialize vector database with sample data
    try:
        initialize_sample_data()
        print("✅ Vector Database Ready")
    except Exception as e:
        print(f"⚠️  Vector Database Warning: {e}")
    
    print(HRAssistantConfig.RESPONSE_SEPARATOR)
    
    # Generate unique session
    session_id = SessionManager.generate_session_id()
    system_config = HRAssistantConfig.get_session_config(session_id)
    
    SessionManager.log_session_event("system_start", {"session_id": session_id})
    return system_config

def process_agent_responses(step_data):
    """Process and display agent responses with enhanced formatting"""
    state_information = step_data[1]
    
    # Define agent types for processing
    active_agents = ["chatbot", "jd_agent", "checklist_agent"]
    
    for agent_name, agent_output in state_information.items():
        if ValidationHelper.validate_agent_name(agent_name):
            display_name = HRAssistantConfig.get_agent_display_name(agent_name)
            print(f"\n🤖 [{display_name}] Response:")
            print(HRAssistantConfig.AGENT_SEPARATOR)
            
            response_messages = agent_output["messages"]
            
            # Handle different message formats
            if isinstance(response_messages, list):
                for individual_msg in response_messages:
                    content = individual_msg if isinstance(individual_msg, str) else individual_msg.content
                    formatted_msg = MessageFormatter.format_agent_response(agent_name, content)
                    print(f"  {formatted_msg}")
            else:
                content = response_messages if isinstance(response_messages, str) else response_messages.content
                formatted_msg = MessageFormatter.format_agent_response(agent_name, content)
                print(f"  {formatted_msg}")
    
    print(HRAssistantConfig.RESPONSE_SEPARATOR)

def main():
    """Main application execution function"""
    try:
        # Initialize system
        config = initialize_hr_system()
        
        # Start conversation flow with sanitized input
        initial_input = ValidationHelper.sanitize_input("Hello, I need assistance with hiring.")
        initial_message = {"messages": [("user", initial_input)]}
        
        # Log user interaction
        SessionManager.log_session_event("user_interaction", {"message": initial_input})
        
        # Process conversation stream
        for conversation_step in graph.stream(initial_message, subgraphs=True, config=config):
            process_agent_responses(conversation_step)
            
    except Exception as e:
        print(f"❌ System Error: {e}")
        SessionManager.log_session_event("system_error", {"error": str(e)})
        sys.exit(1)

if __name__ == "__main__":
    main()

