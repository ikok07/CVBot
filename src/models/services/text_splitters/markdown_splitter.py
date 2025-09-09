import os

from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from src.models.services.text_splitters.base_splitter import BaseSplitter
from src.prompts.markdown_chunker_prompt import MARKDOWN_CHUNKER_PROMPT


class MarkdownSplitter(BaseSplitter):
    async def _get_markdown_chunk_split_points(self, chunked_text: str) -> list[int]:
        llm = ChatOpenAI(model=os.getenv("MARKDOWN_CHUNKS_SPLITTER_MODEL"))
        response = await llm.ainvoke([SystemMessage(content=MARKDOWN_CHUNKER_PROMPT.format(document_text=chunked_text))])

        split_points_str: list[str] = response.content[response.content.find("split_after:") + len("split_after:"):].split(',')
        return [int(split_point.strip()) for split_point in split_points_str]


    async def split(self, file_content: bytes):
        text = file_content.decode("utf-8")

        split_pattern = "\n#"
        chunks = text.split(split_pattern)
        chunked_text = ""
        for i, chunk in enumerate(chunks):
            if chunk.startswith("#"):
                chunk = f"#{chunk}"
            chunked_text += f"<|start_chunk_{i}|>\n{chunk}<|end_chunk_{i}|>"

        split_points = await self._get_markdown_chunk_split_points(chunked_text)

        splitted_documents: list[Document] = []
        last_chunk_end_index = -1
        for split_point in split_points:
            target_end_chunk_tag = f"<|end_chunk_{split_point}|>"
            chunk_end_index = chunked_text.find(target_end_chunk_tag) + len(target_end_chunk_tag)
            splitted_documents.append(
                Document(
                    page_content=chunked_text[
                                 last_chunk_end_index if last_chunk_end_index != -1 else 0
                                 :
                                 chunk_end_index]
                )
            )
            last_chunk_end_index = chunk_end_index

        return splitted_documents, text