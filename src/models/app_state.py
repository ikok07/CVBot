from dataclasses import dataclass

import asyncpg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool


@dataclass
class AppState:
    db_pool = None
    memory: AsyncPostgresSaver = None

app_state = AppState()