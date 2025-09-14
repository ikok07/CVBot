from fastapi import APIRouter

from src.models.responses.generic import GenericResponse
from src.routes.vector_store import vector_store_routes
from src.routes.projects import projects_routes
from src.routes.chatbot import chatbot_routes
from src.routes.webhooks import clerk as clerk_routes

router = APIRouter()

router.include_router(vector_store_routes.router, prefix="/vector-store", tags=["Vector Store"])
router.include_router(projects_routes.router, prefix="/projects", tags=["Projects"])
router.include_router(chatbot_routes.router, prefix="/chatbot", tags=["Chatbot"])
router.include_router(clerk_routes.router, prefix="/webhooks/clerk", tags=["Clerk Webhooks"])

@router.get("/healthcheck")
async def healthcheck():
    return GenericResponse(data={"message": "Server is running normally!"})
