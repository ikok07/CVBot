import json

from langchain_core.messages import ToolMessage

from src.agents.chatbot.state import State
from src.models.agent.agent_source import AgentSource
from src.models.agent.custom_tool_response import CustomToolResponse

class CustomToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    async def __call__(self, state: State):
        if messages := state.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        sources: list[AgentSource] = []
        for tool_call in message.tool_calls:
            tool_result: CustomToolResponse = await self.tools_by_name[tool_call["name"]].ainvoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result.get("data")),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
            if tool_result.get("sources") is not None:
                sources += tool_result.get("sources")

        return State(messages=outputs, sources=sources)