import streamlit as st
from graph.stategraph import graph
import json

st.set_page_config(
    page_title="HR Assistant",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 HR Assistant")
st.markdown("Your AI-powered hiring companion")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial message from assistant
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! How can I assist you with your hiring needs today?"
    })

# Initialize session state for job description
if "job_description" not in st.session_state:
    st.session_state.job_description = None

# Initialize session state for hiring checklist
if "hiring_checklist" not in st.session_state:
    st.session_state.hiring_checklist = None

# Display chat history first
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
user_input = st.chat_input("How can I help you with your hiring needs?")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Process the input through the graph
    try:
        for step in graph.stream({"messages": [("user", user_input)]}, subgraphs=True):
            state_data = step[1]
            
            for node_name, node_response in state_data.items():
                if node_name in ["chatbot", "jd_agent", "checklist_agent"]:
                    messages = node_response.get("messages", "")
                    
                    # Handle different message formats
                    if isinstance(messages, str):
                        content = messages
                    elif isinstance(messages, list):
                        content = " ".join([msg if isinstance(msg, str) else msg.content for msg in messages])
                    else:
                        content = str(messages)
                    
                    # Remove "Chatbot needs clarification: " prefix if present
                    if content.startswith("Chatbot needs clarification: "):
                        content = content[len("Chatbot needs clarification: "):]
                    
                    # Add assistant message to chat history
                    if content.strip():
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": content
                        })
                        
                        # Check if the message contains job description or checklist
                        if "Job Title:" in content:
                            st.session_state.job_description = content
                        elif "Hiring Checklist" in content:
                            st.session_state.hiring_checklist = content
                    
    except Exception as e:
        st.error(f"Error processing input: {str(e)}")
        st.session_state.messages.append({
            "role": "assistant",
            "content": "I apologize, but I encountered an error. Could you please try rephrasing your request?"
        })

# Display job description if available
if st.session_state.job_description:
    st.markdown("---")
    st.subheader("📝 Job Description")
    st.markdown(st.session_state.job_description)

# Display hiring checklist if available
if st.session_state.hiring_checklist:
    st.markdown("---")
    st.subheader("✅ Hiring Checklist")
    st.markdown(st.session_state.hiring_checklist)

# Debug information (collapsed by default)
with st.expander("Debug Information", expanded=False):
    st.write("Session State:", st.session_state)
