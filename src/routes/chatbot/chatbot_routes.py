import time
from typing import Annotated

from fastapi import APIRouter, Body
from langchain_core.messages import HumanMessage, AIMessageChunk
from starlette import status
from starlette.responses import StreamingResponse

from src.agents.chatbot.agent import chatbot_graph
from src.agents.chatbot.state import State
from src.models.body.chatbot import ChatbotInvokeBody
from src.models.errors.api import APIError

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

    graph, tracer = await chatbot_graph(session_id=body.session_id)
    async def generate_response():
        async for chunk, metadata in graph.astream(
                State(
                    messages=[HumanMessage(content=body.message)],
                ),
                stream_mode="messages",
                config={"configurable": {"thread_id": body.session_id}, "callbacks": [tracer]},
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