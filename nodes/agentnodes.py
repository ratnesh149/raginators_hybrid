from langchain_core.messages import HumanMessage, AIMessage
from llm_init import llm
from agents.jd_agent import jd_prompt
from agents.checklist_agent import checklist_prompt
from stateclass import State
from langgraph.types import Command
from typing_extensions import Literal
from tools.vector_tools import vector_tools

def jd_node(state: State) -> Command[Literal['chatbot']]:
    # Extract user messages
    human_messages = [msg.content for msg in state['messages'] if isinstance(msg, HumanMessage)]

    # Build structured message sequence
    messages = [
        ("system", jd_prompt),
        ("human", " ".join(human_messages))
    ]

    # Create LLM with vector tools
    llm_with_tools = llm.bind_tools(vector_tools)
    
    # Call LLM with tools
    response = llm_with_tools.invoke(messages)
    
    # Handle tool calls if present
    if response.tool_calls:
        # Execute tool calls
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Find and execute the tool
            for tool in vector_tools:
                if tool.name == tool_name:
                    try:
                        result = tool._run(**tool_args)
                        tool_results.append(f"Tool {tool_name} result: {result}")
                    except Exception as e:
                        tool_results.append(f"Tool {tool_name} error: {str(e)}")
                    break
        
        # Add tool results to context and get final response
        tool_context = "\n".join(tool_results)
        final_messages = messages + [
            ("assistant", response.content),
            ("human", f"Tool results:\n{tool_context}\n\nNow create the job description based on this information.")
        ]
        
        final_response = llm.invoke(final_messages)
        ai_message = AIMessage(content=final_response.content)
    else:
        # No tool calls, use original response
        ai_message = AIMessage(content=response.content)

    return Command(
        goto="chatbot",
        update={"messages": [ai_message]}
    )


def checklist_node(state: State) -> Command[Literal['chatbot']]:
    # Extract user messages
    human_messages = [msg.content for msg in state['messages'] if isinstance(msg, HumanMessage)]

    messages = [
        ("system", checklist_prompt),
        ("human", " ".join(human_messages))
    ]

    # Create LLM with vector tools for checklist (can use HR policies, interview questions)
    llm_with_tools = llm.bind_tools(vector_tools)
    
    response = llm_with_tools.invoke(messages)
    
    # Handle tool calls if present
    if response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            for tool in vector_tools:
                if tool.name == tool_name:
                    try:
                        result = tool._run(**tool_args)
                        tool_results.append(f"Tool {tool_name} result: {result}")
                    except Exception as e:
                        tool_results.append(f"Tool {tool_name} error: {str(e)}")
                    break
        
        # Add tool results to context and get final response
        tool_context = "\n".join(tool_results)
        final_messages = messages + [
            ("assistant", response.content),
            ("human", f"Tool results:\n{tool_context}\n\nNow create the hiring checklist based on this information.")
        ]
        
        final_response = llm.invoke(final_messages)
        ai_message = AIMessage(content=final_response.content)
    else:
        ai_message = AIMessage(content=response.content)

    return Command(
        goto="chatbot",
        update={"messages": [ai_message]}
    )
