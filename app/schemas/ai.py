from __future__ import annotations

from pydantic import BaseModel, Field


class AICategoryRequest(BaseModel):
    description: str = Field(min_length=1)
