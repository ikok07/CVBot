import os

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from opik.integrations.langchain import OpikTracer

from src.agents.chatbot.nodes import chat_node
from src.agents.chatbot.state import State
from src.agents.chatbot.tools import tools
from src.models.app_state import app_state


async def chatbot_graph():
    state_graph = (StateGraph(State)
    .add_node("chat", chat_node)
    .add_node("tools", ToolNode(tools=tools))
    .add_edge(START, "chat")
    .add_conditional_edges("chat", tools_condition)
    .add_edge("tools", "chat")
    .compile(checkpointer=app_state.memory))
    tracer = OpikTracer(graph=state_graph.get_graph(), project_name=os.getenv("OPIK_PROJECT_NAME"))

    return state_graph, tracer


