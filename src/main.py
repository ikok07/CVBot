import uvicorn
from dotenv import load_dotenv
load_dotenv()

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
    await Tortoise.init(
        config=TORTOISE_CONFIG
    )
    await Tortoise.generate_schemas(safe=True)
    print("ORM Initialized")
    yield
    print("ORM De-Initialized")
    await Tortoise.close_connections()


app = FastAPI(lifespan=lifespan)

app.include_router(v1_routes.router, prefix="/api/v1", tags=["Version 1"])

@app.exception_handler(APIError)
async def api_error_handler(req: Request, err: APIError):
    """ Handle all errors during api route handlers """
    return JSONResponse(
        status_code=err.status_code,
        content={"error": err.message}
    )