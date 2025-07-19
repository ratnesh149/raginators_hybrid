from langgraph.graph import StateGraph, START, END
from stateclass import State
from nodes.chatbot import chatbot_node
from nodes.agentnodes import jd_node, checklist_node, candidate_node
from nodes.human import human_interrupt
from langgraph.checkpoint.memory import MemorySaver


memory = MemorySaver() 

def route_chatbot(state: State):
    """Route based on the chatbot's decision"""
    next_step = state.get("next", "human_interrupt")
    if next_step == "FINISH":
        return END
    return next_step

builder = StateGraph(State)

# Add all nodes
builder.add_node("chatbot", chatbot_node)
builder.add_node("jd_agent", jd_node)
builder.add_node("checklist_agent", checklist_node)
builder.add_node("candidate_agent", candidate_node)
builder.add_node("human_interrupt", human_interrupt)

# Add edges
builder.add_edge(START, "chatbot")

# Add conditional edges from chatbot to route to different agents or END
builder.add_conditional_edges(
    "chatbot",
    route_chatbot,
    {
        "jd_agent": "jd_agent",
        "checklist_agent": "checklist_agent",
        "candidate_agent": "candidate_agent",
        "human_interrupt": "human_interrupt",
        END: END
    }
)

# All other nodes route back to chatbot
builder.add_edge("jd_agent", "chatbot")
builder.add_edge("checklist_agent", "chatbot")
builder.add_edge("candidate_agent", "chatbot")
builder.add_edge("human_interrupt", "chatbot")

graph = builder.compile(checkpointer=memory)