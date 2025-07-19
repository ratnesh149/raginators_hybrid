from langgraph.types import Command
from typing_extensions import TypedDict
from typing import Literal
from llm_init import llm
from stateclass import State

chatbot_prompt = """
You are an HR assistant chatbot that routes requests to specialized agents.

ROUTING RULES:
1. If user provides job requirements and asks for candidates → route to "candidate_agent" ONCE
2. If user asks for job description → route to "jd_agent"  
3. If user asks for hiring checklist → route to "checklist_agent"
4. If you need more info → route to "human_interrupt"
5. If task is complete or agent has provided results → route to "FINISH"

IMPORTANT: 
- When an agent returns results (like candidate shortlist), route to "FINISH"
- Never route to the same agent twice in a row
- If you see "CANDIDATE SHORTLIST" in recent messages, the task is COMPLETE

You must respond in this exact JSON format:
{
  "next": "candidate_agent" | "jd_agent" | "checklist_agent" | "human_interrupt" | "FINISH",
  "messages": "Your message here"
}

EXAMPLES:

User: "Senior frontend developer, React and TypeScript, 5+ years"
Response:
{
  "next": "candidate_agent", 
  "messages": "I'll search our database for senior frontend developers with React and TypeScript experience, 5+ years."
}

After candidate_agent returns results:
{
  "next": "FINISH",
  "messages": "I've found the matching candidates for you. Is there anything else you need help with?"
}

Always check recent messages - if results were already provided, route to FINISH.
"""

class Router(TypedDict):
    next: Literal["jd_agent", "checklist_agent", "candidate_agent", "human_interrupt", "FINISH"]
    messages: str

def chatbot_node(state: State) -> Command[Literal["jd_agent", "checklist_agent", "candidate_agent", "human_interrupt", "__end__"]]:
    messages = [{"role": "system", "content": chatbot_prompt}] + state["messages"]
    
    # Check if we already have results from an agent
    recent_messages = state["messages"][-3:] if len(state["messages"]) > 3 else state["messages"]
    recent_content = " ".join([msg.content for msg in recent_messages if hasattr(msg, 'content')])
    
    # If we already have candidate results, finish
    if "CANDIDATE SHORTLIST" in recent_content:
        return Command(
            goto="__end__",
            update={
                "next": "FINISH", 
                "messages": "I've found the matching candidates for you. Is there anything else you need help with?"
            }
        )
    
    # Check for job requirements pattern
    candidate_keywords = ["react", "typescript", "years", "experience", "senior", "frontend", "developer"]
    has_job_requirements = sum(1 for keyword in candidate_keywords if keyword.lower() in recent_content.lower()) >= 3
    
    # Route to candidate_agent if we have job requirements
    if has_job_requirements:
        return Command(
            goto="candidate_agent",
            update={
                "next": "candidate_agent", 
                "messages": "I'll search our candidate database for the role you described."
            }
        )
    
    # Otherwise use LLM routing
    try:
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        if goto == "FINISH":
            goto = "__end__"
        
        return Command(goto=goto, update={"next": goto, "messages": response["messages"]})
    except Exception as e:
        # Fallback routing
        return Command(
            goto="human_interrupt",
            update={"next": "human_interrupt", "messages": "I need more information to help you properly."}
        )
