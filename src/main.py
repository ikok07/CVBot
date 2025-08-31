from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise import Tortoise

from src.config import TORTOISE_CONFIG
from src.models.errors.api import APIError


@asynccontextmanager
async def lifespan():
    await Tortoise.init(
        config=TORTOISE_CONFIG
    )
    await Tortoise.generate_schemas(safe=True)
    print("ORM Initialized")
    yield
    print("ORM De-Initialized")
    await Tortoise.close_connections()

load_dotenv()

app = FastAPI()

@app.exception_handler(APIError)
async def api_error_handler(req: Request, err: APIError):
    """ Handle all errors during api route handlers """
    return JSONResponse(
        status_code=err.status_code,
        content={"error": err.message}
    )