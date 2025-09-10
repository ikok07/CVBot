import os

from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from opik import track

from src.agents.chatbot.state import State
from src.agents.chatbot.tools import tools
from src.prompts.chatbot_prompt import CHATBOT_SYSTEM_PROMPT

llm = ChatOpenAI(
    model=os.getenv("CHATBOT_MODEL"),
    stream_usage=True
)

llm_with_tools = llm.bind_tools(tools)

async def chat_node(old_state: State):
    return Command(
        update={
            "messages": await llm_with_tools.ainvoke(
                [
                    SystemMessage(content=CHATBOT_SYSTEM_PROMPT),
                ] + old_state["messages"]
            )
        }
    )