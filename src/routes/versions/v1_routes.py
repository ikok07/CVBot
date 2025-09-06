from fastapi import APIRouter
from src.routes.vector_store import vector_store_routes
from src.routes.chatbot import chatbot_routes
from src.routes.webhooks import clerk as clerk_routes

router = APIRouter()

router.include_router(vector_store_routes.router, prefix="/vector-store", tags=["Vector Store"])
router.include_router(chatbot_routes.router, prefix="/chatbot", tags=["Chatbot"])
router.include_router(clerk_routes.router, prefix="/webhooks/clerk", tags=["Clerk Webhooks"])
