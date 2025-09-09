import asyncio
import tempfile
from typing import BinaryIO

from langchain_core.documents import Document
from pydantic import BaseModel

from src.models.services.chunks_enricher import ChunksEnricher
from src.models.services.text_splitters.base_splitter import BaseSplitter
from src.models.services.text_splitters.markdown_splitter import MarkdownSplitter
from src.models.services.text_splitters.pdf_splitter import PDFSplitter
from src.models.services.vector_store import SupportedFileType

from dataclasses import dataclass

@dataclass
class DocumentParseFile:
    file_type: SupportedFileType
    file_content: bytes
    filename: str

@dataclass
class DocumentParseFileInstance:
    file_content: bytes
    file_type: SupportedFileType
    filename: str
    text_splitter: BaseSplitter

@dataclass
class ParsedDocument:
    filename: str
    file_type: SupportedFileType
    chunks: list[Document]

class DocumentParser:
    file_instances: list[DocumentParseFileInstance] = []

    def __init__(self, files: list[DocumentParseFile]):
        text_splitter: BaseSplitter
        for file in files:
            if file.file_type == SupportedFileType.pdf:
                text_splitter = PDFSplitter()
            else:
                text_splitter = MarkdownSplitter()

            self.file_instances.append(
                DocumentParseFileInstance(
                    text_splitter=text_splitter,
                    file_type=file.file_type,
                    file_content=file.file_content,
                    filename=file.filename
                )
            )

    async def _parse_single_file(self, file_instance: DocumentParseFileInstance) -> ParsedDocument:
        file_chunks, markdown = await file_instance.text_splitter.split(file_instance.file_content)

        chunks_enricher = ChunksEnricher(markdown)
        enriched_chunks = await chunks_enricher.enrich_chunks(file_chunks)
        return ParsedDocument(
            file_type=file_instance.file_type,
            filename=file_instance.filename,
            chunks=enriched_chunks
        )

    async def parse_documents(self) -> list[ParsedDocument]:
        response: list[ParsedDocument] = await asyncio.gather(
            *[self._parse_single_file(instance)
            for instance in self.file_instances]
        )

        return response
