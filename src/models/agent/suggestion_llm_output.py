from typing import Annotated

from pydantic import BaseModel, Field


class SuggestionLLMOutput(BaseModel):
    suggestions: list[str] = Field(description="Suggestions for a next questions which could be asked by the visitor")