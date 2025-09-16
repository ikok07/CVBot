from dataclasses import dataclass

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.state import CompiledStateGraph
from opik.integrations.langchain import OpikTracer
from redis import Redis


@dataclass
class AppState:
    db_conn = None
    memory: AsyncPostgresSaver = None
    graph: CompiledStateGraph = None
    tracer: OpikTracer = None
    redis_store: Redis = None

app_state = AppState()