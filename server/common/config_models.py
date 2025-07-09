from typing import List, Optional
from pydantic import BaseModel, Field


class ConfigResponse(BaseModel):
    """Response model for configuration data."""

    id: str
    name: str
    env: str
    useCase: str
    value: str
    description: Optional[str] = None
    createdAt: str


class ConfigListResponse(BaseModel):
    """Response model for paginated list of configurations."""

    items: List[ConfigResponse]
    total: int
    page: int
    pageSize: int
