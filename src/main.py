import os

from dotenv import load_dotenv
from psycopg import AsyncConnection
from starlette import status
from starlette.middleware.cors import CORSMiddleware

load_dotenv()

from src.models.services.vector_store import VectorStore
from src.agents.chatbot.agent import chatbot_graph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from opik import configure
from src.models.app_state import app_state

from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise import Tortoise

from src.config import TORTOISE_CONFIG
from src.models.errors.api import APIError
from src.routes.versions import v1_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_state.db_conn = await AsyncConnection.connect(conninfo=os.getenv("DATABASE_URL"), autocommit=True)
    app_state.memory = AsyncPostgresSaver(conn=app_state.db_conn)

    graph, tracer = await chatbot_graph()
    app_state.graph = graph
    app_state.tracer = tracer

    await app_state.memory.setup()
    await Tortoise.init(
        config=TORTOISE_CONFIG
    )
    await Tortoise.generate_schemas(safe=True)

    print("ORM Initialized")
    yield
    print("ORM De-Initialized")

    await Tortoise.close_connections()
    await app_state.db_conn.close()

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