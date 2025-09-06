from pydantic import BaseModel


class ChatbotInvokeBody(BaseModel):
    message: str
    session_id: str