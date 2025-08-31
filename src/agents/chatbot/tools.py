import os
from typing import Annotated

import requests
from langchain_core.tools import tool

from src.models.services.vector_store import VectorStore

@tool
def send_notification_tool(text: str):
    """
    Use this tool to send a notification when you couldn't answer some question
    :param text: Message informing me about the specific question that couldn't be answered
    """
    try:
        requests.post(os.getenv("PUSHOVER_URL"), data={"token": os.getenv("PUSHOVER_TOKEN"), "user": os.getenv("PUSHOVER_USER"), "message": text})
        return {"status": "success"}
    except Exception as e:
        return {"status": "fail", "error": e}

@tool
def semantic_search(queries: list[str]):
    """
    Use this tool when you want to search more information about something in the vector store

    :param queries: The queries which will be used for semantic search in the vector store
    """

    results = VectorStore.semantic_search(os.getenv("VECTOR_STORE_COLLECTION"), queries)

    return [{
        "query": queries[index],
        "results": [doc.model_dump() for doc in result]
    } for index, result in enumerate(results)]

tools = [send_notification_tool, semantic_search]