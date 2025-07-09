from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class PromptType(str, Enum):
    """Enumeration of possible prompt types."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class PromptBase(BaseModel):
    """Base model for prompt-related schemas."""

    name: str = Field(..., description="Name of the prompt")
    description: Optional[str] = Field(None, description="Description of the prompt")
    content: str = Field(..., description="Content of the prompt")
    is_active: bool = Field(True, description="Whether the prompt is active")
    use_case: Optional[str] = Field(None, description="Use case for the prompt")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    env: Optional[str] = Field(
        None, description="Environment for the prompt (e.g., dev, staging, prod)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the prompt"
    )


class PromptCreate(PromptBase):
    """Schema for creating a new prompt."""

    pass


class PromptUpdate(BaseModel):
    """Schema for updating an existing prompt."""

    name: Optional[str] = Field(None, description="Name of the prompt")
    description: Optional[str] = Field(None, description="Description of the prompt")
    content: Optional[str] = Field(None, description="Content of the prompt")
    prompt_type: Optional[PromptType] = Field(None, description="Type of the prompt")
    is_active: Optional[bool] = Field(None, description="Whether the prompt is active")
    use_case: Optional[str] = Field(None, description="Use case for the prompt")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    env: Optional[str] = Field(
        None, description="Environment for the prompt (e.g., dev, staging, prod)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the prompt"
    )


class PromptResponse(PromptBase):
    """Schema for prompt response."""

    id: str = Field(..., description="Unique identifier for the prompt")
    createdAt: datetime = Field(
        ..., description="Timestamp when the prompt was created"
    )

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class PromptListResponse(BaseModel):
    """Schema for paginated list of prompts."""

    items: List[PromptResponse] = Field(..., description="List of prompts")
    total: int = Field(..., description="Total number of prompts")
    page: int = Field(..., description="Current page number")
    pageSize: int = Field(..., description="Number of items per page")
