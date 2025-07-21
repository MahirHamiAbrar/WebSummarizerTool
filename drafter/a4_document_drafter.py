# import os
# from dotenv import load_dotenv
# from typing import Annotated, Sequence, TypedDict

# from langchain_groq import ChatGroq
# from langchain_core.messages import (
#     BaseMessage,
#     AIMessage,
#     HumanMessage,
#     SystemMessage,
#     ToolMessage
# )

# from langchain_core.tools import tool
# from langgraph.prebuilt import ToolNode

# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages

# load_dotenv()


# document_draft: str = ""

# # Create tools
# @tool
# def update_draft(content: str) -> str:
#     """Updates the draft content.

#     Args:
#         content (str): file draft content
#     """
#     global document_draft
#     document_draft = content
#     print(document_draft)
#     return f"Successfully updated the following document draft:\n\n----- {content}.\n\n-----Now ask the user if they are satisfied with it or needs editing."

# @tool
# def save_draft(content: str, filename: str) -> str:
#     """Saves the created draft in a file.

#     Args:
#         content (str): file draft content
#         filename (str): filename with a `.txt` extension
#     """
#     try:
#         with open(filename, 'w') as file:
#             file.write(content)
#     except Exception as e:
#         return f"Failed to save file due to the error: {str(e)}"
#     return "Successfully saved the file content."

# @tool
# def read_document(filename: str) -> str:
#     """Use this function to read the given document"""
#     if not os.path.exists(filename):
#         return f"{filename} does not exist."
    
#     with open(filename, 'w') as file:
#         return f"File: {filename} contains the following content:\n\n{file.read()}"


# # tools = [update_draft, save_draft]
# tools = [read_document, save_draft]
# llm = ChatGroq(model="llama-3.3-70b-versatile").bind_tools(tools)


# # Create the state schema
# class AgentState(TypedDict):
#     messages: Annotated[Sequence[BaseMessage], add_messages]


# # Create Nodes
# def agent_node(state: AgentState) -> AgentState:
#     """LLM that makes decisions or generate responses."""

#     if not state["messages"]:
#                 # - `update_draft`: to create or update a document/content asked by the user.
#         system_prompt = SystemMessage(
#             """You are an AI assistant designed to help users read, create, edit, and update drafts through natural conversation. You have access to the tools: read_document, save_draft (which saves the current version of the draft. You must not invoke this tool unless the user explicitly instructs you to save.)

# Core Behavior:
#     - Begin by asking thoughtful, open-ended questions to understand the user’s intent, context, and goals for the draft.
#     - Collaborate conversationally with the user to generate or refine the content step by step. Maintain a helpful, proactive tone while respecting user autonomy.
#     - After each update or suggestion, confirm with the user if they'd like further edits, additions, or changes.

# At no point should you assume the user wants to save the draft unless they clearly say so. Wait for explicit instructions like:
#     - “Save this”
#     - “Please save the draft”
#     - “You can now use the save_draft tool”
#     - “Store this version”

# Guidelines:
#     - If the user says something vague like “Looks good” or “That’s fine,” do not trigger save_draft unless followed by an explicit save instruction.
#     - If the user says “Save it for later,” or “Let’s keep this,” clarify: “Would you like me to save this draft now?”
#     - You can keep track of different versions conversationally (e.g., “This is Version 2 with the changes you asked for”), but saving must still be user-confirmed.

# Only use the `save_draft` tool once the user responds with an explicit "yes" or a direct save command."""
#         )
#         state["messages"] = [system_prompt]

#     ai_msg = llm.invoke(state["messages"])
#     return {"messages": ai_msg}


# def should_use_tool(state: AgentState) -> str:
#     """Decide wheather to use tool or not."""
#     ai_msg: AIMessage = state["messages"][-1]

#     if not ai_msg.tool_calls:
#         return "no_tools"
#     return "use_tools"


# # create the graph
# graph = StateGraph(AgentState)
# tools_node = ToolNode(tools)

# graph.add_node("agent", agent_node)
# graph.add_node("tools", tools_node)

# graph.add_edge(START, "agent")
# graph.add_edge("tools", "agent")

# graph.add_conditional_edges(
#     "agent",
#     should_use_tool,
#     {
#         "use_tools": "tools",
#         "no_tools": END,
#     }
# )

# agent = graph.compile()
# # agent.get_graph().draw_png("drafter_graph.png")


# def chat() -> None:
#     """Chat with the AI Agent"""

#     conversation = []
#     query = input("Ask Anything: ").strip()

#     while query.lower() != "/q":    # type "/q" to exit
#         conversation.append(HumanMessage(query))
        
#         message_list = agent.invoke({ "messages": conversation })
#         ai_response: AIMessage = message_list["messages"][-1]

#         print(f"Assistant: {ai_response.content}")

#         query = input("Ask Anything: ").strip()


# if __name__ == '__main__':
#     chat()

import os
from dotenv import load_dotenv
from typing import Annotated, Sequence, TypedDict

from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv()

# Global variable to hold the current document draft
document_draft: str = ""

# Tool: Update the draft content (currently unused but can be added later)
@tool
def update_draft(content: str) -> str:
    """Updates the draft content."""
    global document_draft
    document_draft = content
    print(document_draft)
    return f"Successfully updated the following document draft:\n\n----- {content}.\n\n-----Now ask the user if they are satisfied with it or needs editing."

# Tool: Save the draft to a file
@tool
def save_draft(content: str, filename: str) -> str:
    """Use this to save a document. ASK FOR PERMISSION FROM THE USER BEFORE USING THIS FUNCTION."""
    try:
        with open(filename, 'w') as file:
            file.write(content)
    except Exception as e:
        return f"Failed to save file due to the error: {str(e)}"
    return "Successfully saved the file content."

# Tool: Read content from an existing document
@tool
def read_document(filename: str) -> str:
    """Use this function to read the given document."""
    if not os.path.exists(filename):
        return f"{filename} does not exist."

    with open(filename, 'r') as file:
        return f"File: {filename} contains the following content:\n\n{file.read()}"

# Define the tools to be used
TOOLS = [read_document, save_draft]
# llm = ChatGroq(model="llama-3.3-70b-versatile").bind_tools(TOOLS)
llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct").bind_tools(TOOLS)
# llm = ChatOllama(model="qwen2.5:14b").bind_tools(TOOLS)
# llm = ChatOllama(model="llama3.2:3b").bind_tools(TOOLS)

# Define state schema
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Agent node: Handles conversation with LLM
def agent_node(state: AgentState) -> AgentState:
    if not state["messages"]:
        state["messages"] = [
            SystemMessage(
                """
You are an AI assistant designed to help users read, create, edit, and update drafts through natural conversation. 
You only have access to the tools: read_document and save_draft.

!! Important Rule !!
Never use the save_draft tool unless the user gives an **explicit instruction** to save. Wait for clear commands like:
- "Save this"
- "Please save the draft"
- "You can now use the save_draft tool"
- "Store this version"

Behavior:
- Begin by asking open-ended questions to understand the user’s intent.
- Collaborate step-by-step to generate or revise content.
- After each update, ask if the user is satisfied or wants changes.

Guidelines:
- Never assume the user wants to save.
- Clarify vague statements like "Looks good" by asking: "Would you like me to save this draft now?"
- You may track versions conversationally but must wait for explicit permission before saving.
                """
            )
        ]

    ai_msg = llm.invoke(state["messages"])
    return {"messages": ai_msg}

# Decision function: whether to use a tool or not
def should_use_tool(state: AgentState) -> str:
    ai_msg: AIMessage = state["messages"][-1]
    return "use_tools" if ai_msg.tool_calls else "no_tools"

# Construct the graph
graph = StateGraph(AgentState)
tool_node = ToolNode(TOOLS)

graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")

graph.add_conditional_edges("agent", should_use_tool, {
    "use_tools": "tools",
    "no_tools": END,
})

agent = graph.compile()

# Chat loop
def chat() -> None:
    conversation = []
    query = input("Ask Anything: ").strip()

    while query.lower() != "/q":  # type "/q" to exit
        conversation.append(HumanMessage(query))
        result = agent.invoke({"messages": conversation})
        ai_response: AIMessage = result["messages"][-1]
        print(f"Assistant: {ai_response.content}")
        query = input("Ask Anything: ").strip()

if __name__ == '__main__':
    chat()
