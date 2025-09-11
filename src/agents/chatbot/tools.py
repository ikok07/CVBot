import os
from dataclasses import asdict

import requests
from langchain_core.tools import tool
from opik import track

from src.models.services.vector_store import VectorStore

@tool
def send_notification_tool(text: str):
    """
    Use this tool to send a notification after you search the vector store, and you couldn't answer some question
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
    Search for relevant information in the knowledge base using semantic similarity.

    Use this tool FIRST when the user asks questions that might be answered by stored documents.
    Always try this tool before using send_notification_tool.

    The search queries SHOULD be only in ENGLISH.

    :param queries: List of search queries to find relevant information.
                   Use multiple related queries to get comprehensive results.
    """

    results = VectorStore.semantic_search(os.getenv("VECTOR_STORE_COLLECTION"), queries)

    return [{
        "query": queries[index],
        "results": [asdict(doc) for doc in result]
    } for index, result in enumerate(results)]

tools = [send_notification_tool, semantic_search]