import os

import asyncpg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
# from opik import configure

from src.agents.chatbot.nodes import chat_node
from src.agents.chatbot.state import State

# configure()

async def chatbot_graph():
    conn = await asyncpg.connect(dsn=os.getenv("DATABASE_URL"))
    memory = AsyncPostgresSaver(conn=conn)
    return (
        StateGraph(State)
        .add_node("chat", chat_node)
        .add_node("tools", ToolNode)
        .add_edge(START, "chat")
        .add_conditional_edges("chat", tools_condition, {"tools": "tools", END: END})
        .compile(checkpointer=memory)
    )


