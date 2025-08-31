import os

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from opik import configure

from src.agents.chatbot.nodes import chat_node
from src.agents.chatbot.state import State

configure()

async def chatbot_graph():
    with AsyncPostgresSaver.from_conn_string(os.getenv("DATABASE_URL")) as memory:
        return (
            StateGraph(State)
            .add_node("chat", chat_node)
            .add_node("tools", ToolNode)
            .add_edge(START, "chat")
            .add_conditional_edges("chat", tools_condition, {"tools": "tools"})
            .compile(checkpointer=memory)
        )


