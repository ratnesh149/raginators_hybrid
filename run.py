#!/usr/bin/env python3
"""
Simple HR Assistant Runner
Works with the current graph structure
"""

from graph.stategraph import graph
from langchain_core.messages import HumanMessage, AIMessage
import sys

def main():
    """Main conversation loop"""
    print("🚀 HR Assistant Starting...")
    print("📊 Initializing Vector Database...")
    
    # Initialize vector database
    try:
        from tools.document_processor import initialize_sample_data
        initialize_sample_data()
        print("✅ Vector Database Ready")
    except Exception as e:
        print(f"⚠️  Vector Database Warning: {e}")
    
    print("=" * 50)
    print("💬 Chat with your HR Assistant!")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    # Configuration
    config = {
        "configurable": {"thread_id": "hr_session"},
        "recursion_limit": 10
    }
    
    # Initialize conversation state
    state = {"messages": []}
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Thanks for using HR Assistant!")
                break
            
            if not user_input:
                continue
            
            # Add user message to state
            state["messages"].append(HumanMessage(content=user_input))
            
            print("\n🤖 Assistant:")
            print("-" * 40)
            
            # Process through the graph
            response_received = False
            
            try:
                for step in graph.stream(state, config=config):
                    for node_name, node_output in step.items():
                        if "messages" in node_output and node_output["messages"]:
                            latest_message = node_output["messages"][-1]
                            
                            if hasattr(latest_message, 'content'):
                                content = latest_message.content
                                print(content)
                                
                                # Update state with the response
                                state["messages"].extend(node_output["messages"])
                                response_received = True
                                
                                # If we got a candidate shortlist, we're done with this request
                                if "CANDIDATE SHORTLIST" in content:
                                    break
                    
                    if response_received:
                        break
                        
            except Exception as e:
                print(f"❌ Error processing request: {e}")
                print("Please try again with a different request.")
            
            if not response_received:
                print("⚠️  No response received. Please try rephrasing your request.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
