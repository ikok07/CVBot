import asyncio
import os

from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from src.prompts.chunks_enricher_prompt import CHUNKS_ENRICHER_PROMPT


class ChunksEnricher:
    llm = ChatOpenAI(model=os.getenv("CHUNKS_ENRICHER_MODEL"))

    def __init__(self, whole_document: str):
        self.whole_document = whole_document

    async def _enrich_single_chunk(self, chunk: str) -> str:
        response = await self.llm.ainvoke([SystemMessage(content=CHUNKS_ENRICHER_PROMPT.format(document_text=self.whole_document, chunk_text=chunk))])
        return f"<chunk_context>{response.content}</chunk_context><chunk>{chunk}</chunk>"

    async def enrich_chunks(self, chunks: list[Document]):
        response: list[str] = await asyncio.gather(*[
            self._enrich_single_chunk(chunk.page_content)
            for chunk in chunks
        ])
        return [Document(page_content=response_chunk) for response_chunk in response]