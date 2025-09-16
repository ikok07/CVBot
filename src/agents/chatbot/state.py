from typing import Annotated

from langgraph.graph import MessagesState

from src.models.agent.agent_source import AgentSource
from operator import add

class State(MessagesState):
    sources: list[AgentSource]
    pass