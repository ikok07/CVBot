import asyncio
import json
import os
import pprint
import time
from typing import Annotated

from fastapi import APIRouter, Body
from fastapi.params import Query, Depends
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk
from starlette import status
from starlette.responses import StreamingResponse

from src.agents.chatbot.agent import chatbot_graph
from src.agents.chatbot.state import State
from src.agents.chatbot.tools import get_all_projects
from src.models.agent.agent_source import AgentSource
from src.models.app_state import app_state
from src.models.body.chatbot import ChatbotInvokeBody
from src.models.db import MessageSource, MessageSourceSchema
from src.models.errors.api import APIError
from src.models.responses.generic import GenericResponse
from src.routes.dependencies.rate_limit import rate_limit
from src.utils.message_to_role import message_to_role

router = APIRouter()

async def test():
    time.sleep(4)

@router.post("/invoke")
async def invoke_chatbot(body: Annotated[ChatbotInvokeBody, Body()], _ = Depends(rate_limit(limit=20, window_seconds=60))):

    if len(body.message) == 0:
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Message should not be empty!"
        )

    async def generate_response():
        try:
            async for chunk, metadata in app_state.graph.astream(
                    State(
                        messages=[HumanMessage(content=body.message)],
                        sources=[]
                    ),
                    stream_mode="messages",
                    config={"configurable": {"thread_id": body.session_id}, "callbacks": [app_state.tracer]},
            ):
                if not isinstance(chunk, AIMessageChunk):
                    continue
                message_chunk: AIMessageChunk = chunk
                if message_chunk.content :
                    yield f"data: {json.dumps({"content": message_chunk.content, "type": "content"}, ensure_ascii=False)}\n\n"

            final_state = await app_state.graph.aget_state(config={"configurable": {"thread_id": body.session_id}})

            if "sources" in final_state.values:
                sources: list[AgentSource] = final_state.values["sources"]

                await asyncio.gather(
                    *[MessageSource(name=source.name, url=source.url, message_id=final_state.values["messages"][-1].id).save() for source in sources]
                )

                if sources:
                    yield f"data: {json.dumps({"content": [source.model_dump() for source in sources], "type": "sources"})}\n\n"

        except Exception as e:
            print("Chatbot message generator method failed!")
            print(e)
            yield f"data: {json.dumps({"content": "Something went wrong with the response!", "type": "error"})}\n\n"


    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream"
    )

@router.get("/history")
async def get_history(session_id: Annotated[str, Query()]):
    messages = await app_state.memory.aget({"configurable": {"thread_id": session_id}})

    if not messages:
        default_message = os.getenv("DEFAULT_CHATBOT_MESSAGE", "Hello there!")
        return GenericResponse(data=[{"id": "default", "role": "assistant", "content": default_message, "sources": []}])

    messages_dict = [
        {"id": message.id, "role": message_to_role(message), "content": message.content, "sources": [(await MessageSourceSchema.from_tortoise_orm(source)).model_dump() for source in await MessageSource.filter(message_id=message.id)]}
        for message in messages["channel_values"]["messages"]
    ]

    return GenericResponse(data=messages_dict)