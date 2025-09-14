from typing import Optional, TypedDict

from src.models.agent.agent_source import AgentSource


class CustomToolResponse(TypedDict):
    data: dict | list[dict]
    sources: Optional[list[AgentSource]]