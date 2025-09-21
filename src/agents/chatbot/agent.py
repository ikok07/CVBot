import asyncio
import json
import os

from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from opik.integrations.langchain import OpikTracer

from src.agents.chatbot.nodes import chat_node, suggestions_generation_node
from src.agents.chatbot.state import State
from src.agents.chatbot.tools import tools
from src.agents.common.nodes.CustomToolNode import CustomToolNode
from src.models.agent.agent_source import AgentSource
from src.models.app_state import app_state
from src.models.db import MessageSource

async def chatbot_graph():
    state_graph = (StateGraph(State)
    .add_node("chat", chat_node)
    .add_node("suggestions", suggestions_generation_node)
    .add_node("tools", CustomToolNode(tools=tools))
    .add_edge(START, "chat")
    .add_conditional_edges("chat", tools_condition, {"tools": "tools", END: "suggestions"})
    .add_edge("tools", "chat")
    .add_edge("suggestions", END)
    .compile(checkpointer=app_state.memory))
    tracer = OpikTracer(graph=state_graph.get_graph(), project_name=os.getenv("OPIK_PROJECT_NAME"))

    return state_graph, tracer

async def generate_response(message: str, thread_id: str):
    try:
        async for chunk, metadata in app_state.graph.astream(
                State(
                    messages=[HumanMessage(content=message)],
                    sources=[]
                ),
                stream_mode="messages",
                config={"configurable": {"thread_id": thread_id}, "callbacks": [app_state.tracer]},
        ):
            disallowed_nodes = ["suggestions"]
            if not isinstance(chunk, AIMessageChunk) or metadata["langgraph_node"] in disallowed_nodes:
                continue
            message_chunk: AIMessageChunk = chunk

            if message_chunk.content :
                yield f"data: {json.dumps({"content": message_chunk.content, "type": "content"}, ensure_ascii=False)}\n\n"

        final_state = await app_state.graph.aget_state(config={"configurable": {"thread_id": thread_id}})

        if "sources" in final_state.values:
            sources: list[AgentSource] = final_state.values["sources"]

            await asyncio.gather(
                *[MessageSource(name=source.name, url=source.url, message_id=final_state.values["messages"][-1].id).save() for source in sources]
            )

            if sources:
                yield f"data: {json.dumps({"content": [source.model_dump() for source in sources], "type": "sources"})}\n\n"

        if "question_suggestions" in final_state.values:
            suggestions: list[str] = final_state.values["question_suggestions"]
            yield f"data: {json.dumps({"content": [suggestion for suggestion in suggestions[:3]], "type": "suggestion"}, ensure_ascii=False)}\n\n"

    except Exception as e:
        print("Chatbot message generator method failed!")
        print(e)
        yield f"data: {json.dumps({"content": "Something went wrong with the response!", "type": "error"})}\n\n"


