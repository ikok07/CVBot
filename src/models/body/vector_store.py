from pydantic import BaseModel


class VectorStoreSemanticSearchBody(BaseModel):
    queries: list[str]