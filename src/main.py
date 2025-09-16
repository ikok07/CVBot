import os

from dotenv import load_dotenv
load_dotenv()

from src.lifespan import lifespan
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from src.models.services.vector_store import VectorStore
from opik import configure

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.models.errors.api import APIError
from src.routes.versions import v1_routes


configure(api_key=os.getenv("OPIK_API_KEY"), workspace=os.getenv("OPIK_WORKSPACE_NAME"), force=True)
VectorStore.init()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(v1_routes.router, prefix="/api/v1", tags=["Version 1"])

@app.exception_handler(APIError)
async def api_error_handler(req: Request, err: APIError):
    """ Handle all errors during api route handlers """
    return JSONResponse(
        status_code=err.status_code,
        content={"error": err.message}
    )

@app.exception_handler(Exception)
async def generic_error_handler(req: Request, err: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(err)}
    )