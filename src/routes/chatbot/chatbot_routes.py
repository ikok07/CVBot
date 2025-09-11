import time
from typing import Annotated

from fastapi import APIRouter, Body
from fastapi.params import Query
from langchain_core.messages import HumanMessage, AIMessageChunk
from starlette import status
from starlette.responses import StreamingResponse

from src.agents.chatbot.agent import chatbot_graph
from src.agents.chatbot.state import State
from src.models.app_state import app_state
from src.models.body.chatbot import ChatbotInvokeBody
from src.models.errors.api import APIError
from src.models.responses.generic import GenericResponse

router = APIRouter()

async def test():
    time.sleep(4)

@router.post("/invoke")
async def invoke_chatbot(body: Annotated[ChatbotInvokeBody, Body()]):

    if len(body.message) == 0:
        raise APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Message should not be empty!"
        )


    async def generate_response():
        async for chunk, metadata in app_state.graph.astream(
                State(
                    messages=[HumanMessage(content=body.message)],
                ),
                stream_mode="messages",
                config={"configurable": {"thread_id": body.session_id}, "callbacks": [app_state.tracer]},
        ):
            if not isinstance(chunk, AIMessageChunk):
                continue
            message_chunk: AIMessageChunk = chunk
            if message_chunk.content :
                yield f"{message_chunk.content}\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/plain"
    )

@router.get("/history")
async def get_history(session_id: Annotated[str, Query()]):
    messages = await app_state.memory.aget({"configurable": {"thread_id": session_id}})
    print()
    if not messages:
        raise APIError(status_code=status.HTTP_404_NOT_FOUND, message="Session not found!")

    messages_dict = [
        {"role": "user" if isinstance(message, HumanMessage) else "assistant", "content": message.content}
        for message in messages["channel_values"]["messages"]
    ]

    return GenericResponse(data=messages_dict)