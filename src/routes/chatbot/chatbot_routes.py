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

from src.agents.chatbot.agent import chatbot_graph, generate_response
from src.agents.chatbot.state import State
from src.agents.chatbot.tools import get_all_projects
from src.models.agent.agent_source import AgentSource
from src.models.app_state import app_state
from src.models.body.chatbot import ChatbotInvokeBody
from src.models.db import MessageSource, MessageSourceSchema
from src.models.errors.api import APIError
from src.models.i18n.supported_languages import SupportedLanguage
from src.models.responses.generic import GenericResponse
from src.routes.dependencies.locale_parser import locale_parser
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

    return StreamingResponse(
        generate_response(message=body.message, thread_id=body.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/history")
async def get_history(session_id: Annotated[str, Query()], language = Depends(locale_parser)):
    messages = await app_state.memory.aget({"configurable": {"thread_id": session_id}})

    if not messages:
        default_message = os.getenv(
            "DEFAULT_CHATBOT_MESSAGE_BG" if language == SupportedLanguage.bg else "DEFAULT_CHATBOT_MESSAGE_EN",
            "Hello there!"
        )
        return GenericResponse(data=[{"id": "default", "role": "assistant", "content": default_message, "sources": []}])

    messages_dict = [
        {"id": message.id, "role": message_to_role(message), "content": message.content, "sources": [(await MessageSourceSchema.from_tortoise_orm(source)).model_dump() for source in await MessageSource.filter(message_id=message.id)]}
        for message in messages["channel_values"]["messages"]
    ]

    return GenericResponse(data=messages_dict)