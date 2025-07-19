from langgraph.types import Command
from typing_extensions import Literal
from stateclass import State
from langchain_core.messages import HumanMessage

def human_interrupt(state: State) -> Command[Literal['chatbot']]:
    query = state['messages'][-1].content
    # print(f"Chatbot needs clarification: {query}")
    user_input = input("user: ")
    
    # Create proper HumanMessage
    human_message = HumanMessage(content=user_input)
    
    return Command(goto="chatbot", update={"messages": [human_message]})
