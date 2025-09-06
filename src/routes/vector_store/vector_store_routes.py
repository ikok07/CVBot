import hashlib
import io
import os
from typing import Annotated

import PyPDF2
from clerk_backend_api import User
from fastapi import APIRouter, UploadFile, Depends, Query, Form
from langchain_core.documents import Document
from starlette import status

from src.models.db.profiles import Profile
from src.models.errors.api import APIError
from src.models.responses.generic import GenericResponse
from src.models.services.text_splitter import TextSplitter, ChunkingStrategy
from src.models.services.vector_store import VectorStore, StoreFullFile, SupportedFileType
from src.routes.dependencies.protect import protect_dependency

router = APIRouter()

@router.get("/retrieve-files")
async def retrieve_files(userdata: tuple[User, Profile] = Depends(protect_dependency)):
    try:
        store_docs = VectorStore.get_all_docs(collection_name=os.getenv("VECTOR_STORE_COLLECTION"))
        full_files: list[StoreFullFile] = []
        for store_document in store_docs:
            if not store_document.metadata["filename"] in [file.filename for file in full_files]:
                full_files.append(
                    StoreFullFile(
                        filename=store_document.metadata["filename"],
                        filetype=store_document.metadata["filetype"],
                        chunking_strategy=store_document.metadata["chunking_strategy"],
                        created_at=store_document.metadata["created_at"]
                    )
                )

        return GenericResponse(
            data=[dict(file) for file in full_files]
        )
    except ValueError as e:
        print("Collection not found!")
        raise APIError(status.HTTP_500_INTERNAL_SERVER_ERROR, "Collection not found")
    except Exception as e:
        print(e)
        raise APIError(status.HTTP_500_INTERNAL_SERVER_ERROR, "Unknown error occurred")

@router.post("/store-files")
async def store_files(files: list[UploadFile], semantic_split: Annotated[bool, Form()] = False, userdata: tuple[User, Profile] = Depends(protect_dependency)):

    # Check for file support before doing anything
    for file in files:
        if not file.content_type in SupportedFileType:
            return APIError(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, message=f"Supported file formats: {", ".join(SupportedFileType)}")

    for file in files:
        store_files = VectorStore.get_docs_by_filename(file.filename, os.getenv("VECTOR_STORE_COLLECTION"))
        if len(store_files) > 0:
            raise APIError(status.HTTP_400_BAD_REQUEST, message=f"({file.filename}): File already exists")

        chunks: list[Document] = []
        chunking_strategy: ChunkingStrategy = ChunkingStrategy.recursive_char_splitter
        if file.content_type == SupportedFileType.pdf:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(await file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n\n"

            chunking_strategy = ChunkingStrategy.semantic_splitter
            chunks += TextSplitter.semantic_split([text])
        elif semantic_split:
            chunking_strategy = ChunkingStrategy.semantic_splitter
            chunks += TextSplitter.semantic_split([(await file.read()).decode("utf-8")])
        elif file.content_type == SupportedFileType.markdown:
            chunking_strategy = ChunkingStrategy.markdown_splitter
            chunks += TextSplitter.markdown_split([(await file.read()).decode("utf-8")])
        else:
            chunks += TextSplitter.generic_split([(await file.read()).decode("utf-8")])

        VectorStore.insert_docs(
            docs=[chunk.page_content for chunk in chunks],
            collection_name=os.getenv("VECTOR_STORE_COLLECTION"),
            filename=file.filename,
            filetype=str(file.content_type),
            chunking_strategy=chunking_strategy,
            custom_ids=[hashlib.sha256(chunk.page_content.encode("utf-8")).hexdigest() for chunk in chunks]
        )

    return GenericResponse()

@router.delete("/delete-files")
async def delete_files(filenames: Annotated[list[str], Query()], userdata: tuple[User, Profile] = Depends(protect_dependency)):
    for filename in filenames:
        VectorStore.delete_document_by_name(filename, collection_name=os.getenv("VECTOR_STORE_COLLECTION"))

    return GenericResponse()