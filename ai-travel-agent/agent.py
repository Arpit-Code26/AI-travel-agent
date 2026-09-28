from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from tools import search_flights_and_hotels, send_itinerary_email
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

search_node = ToolNode(tools=[search_flights_and_hotels])
email_node = ToolNode(tools=[send_itinerary_email])

# Removed temperature parameter to prevent runtime warnings
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    max_retries=5,
)
llm_with_tools = llm.bind_tools([search_flights_and_hotels, send_itinerary_email])

system_instruction = SystemMessage(
    content=(
        "You are an expert AI Travel Agent.\n\n"
        "FORMATTING RULES:\n"
        "1. Write all responses and itineraries in clean, standard Markdown.\n"
        "2. Never use raw HTML tags such as <div>, <p>, <span>, or <style>.\n"
        "3. Organize details using clear headers (##, ###), bullet points, and bold text so it reads easily on screen.\n\n"
        "WORKFLOW RULES:\n"
        "1. If live search data is needed, call search_flights_and_hotels.\n"
        "2. Always output the full itinerary directly in your chat response so the user can review it.\n"
        "3. If an email address is provided, pass the plain Markdown text directly into send_itinerary_email."
    )
)

def chatbot_node(state: AgentState):
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [system_instruction] + messages
    return {"messages": [llm_with_tools.invoke(messages)]}

def route_tools(state: AgentState):
    last_message = state["messages"][-1]
    if not getattr(last_message, "tool_calls", None):
        return END
    
    if last_message.tool_calls[0]["name"] == "send_itinerary_email":
        return "email_node"
    return "search_node"

graph_builder = StateGraph(AgentState)
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_node("search_node", search_node)
graph_builder.add_node("email_node", email_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot", 
    route_tools, 
    {"search_node": "search_node", "email_node": "email_node", END: END}
)
graph_builder.add_edge("search_node", "chatbot")
graph_builder.add_edge("email_node", "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(
    checkpointer=memory,
    interrupt_before=["email_node"]
)