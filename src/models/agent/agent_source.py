from typing import Optional

from pydantic import BaseModel

class AgentSource(BaseModel):
    name: str
    url: Optional[str]