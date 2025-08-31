import os

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command

from src.agents.chatbot.state import State
from src.agents.chatbot.tools import tools

llm = ChatOpenAI(
    model=os.getenv("CHATBOT_MODEL")
)
llm_with_tools = llm.bind_tools(tools)

async def chat_node(old_state: State):
    return Command(
        update={
            "message": await llm.invoke(
                [
                    SystemMessage(content=os.getenv("CHATBOT_SYSTEM_PROMPT")),
                ] + old_state["messages"]
            )
        }
    )