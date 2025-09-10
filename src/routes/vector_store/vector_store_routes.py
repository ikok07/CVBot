import hashlib
import os
from typing import Annotated

from clerk_backend_api import User
from fastapi import APIRouter, UploadFile, Depends, Query, Form, Body
from starlette import status

from src.models.body.vector_store import VectorStoreSemanticSearchBody
from src.models.db.profiles import Profile
from src.models.errors.api import APIError
from src.models.responses.generic import GenericResponse
from src.models.services.document_parser import DocumentParser, DocumentParseFile
from src.models.services.vector_store import VectorStore, StoreFullFile, SupportedFileType
from src.routes.dependencies.protect import protect_dependency

router = APIRouter()

@router.post("/semantic-search")
async def semantic_search(body: Annotated[VectorStoreSemanticSearchBody, Body()], userdata: tuple[User, Profile] = Depends(protect_dependency)):
    try:
        results = VectorStore.semantic_search(
            collection_name=os.getenv("VECTOR_STORE_COLLECTION"),
            texts=body.queries,
            n_results=5
        )

        return GenericResponse(data={"results": [[doc.model_dump() for doc in result] for result in results]})
    except Exception as e:
        print(e)
        raise APIError(status.HTTP_500_INTERNAL_SERVER_ERROR, "Unknown error occurred")

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
async def store_files(files: list[UploadFile], userdata: tuple[User, Profile] = Depends(protect_dependency)):

    # Check for file support before doing anything
    for file in files:
        if not file.content_type in SupportedFileType:
            return APIError(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, message=f"Supported file formats: {", ".join(SupportedFileType)}")

    document_parser = DocumentParser(files=[DocumentParseFile(file_type=file.content_type, file_content=await file.read(), filename=file.filename) for file in files])
    parsed_docs = await document_parser.parse_documents()

    for parsed_doc in parsed_docs:
        VectorStore.insert_docs(
            docs=[chunk.page_content for chunk in parsed_doc.chunks],
            collection_name=os.getenv("VECTOR_STORE_COLLECTION"),
            filename=parsed_doc.filename,
            filetype=str(parsed_doc.file_type),
            custom_ids=[hashlib.sha256(chunk.page_content.encode("utf-8")).hexdigest() for chunk in parsed_doc.chunks]
        )

    return GenericResponse()

@router.delete("/delete-files")
async def delete_files(filenames: Annotated[list[str], Query()], userdata: tuple[User, Profile] = Depends(protect_dependency)):
    for filename in filenames:
        VectorStore.delete_document_by_name(filename, collection_name=os.getenv("VECTOR_STORE_COLLECTION"))

    return GenericResponse()