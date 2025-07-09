from typing import Any, Awaitable, Callable, List, Mapping, Optional

from pipecat.processors.frameworks.rtvi import RTVIMessage, RTVIServiceConfig
from pydantic import BaseModel, Field


class BotSystemPrompt(BaseModel):
    language: str = Field(default="", description="Language of the conversation")
    scenario_title: str = Field(
        default="Complaint", description="Title of the scenario"
    )
    scenario: str = Field(default="", description="Scenario detail")
    level: str = Field(default="New Hire", description="Agent level")


class BotConfig(BaseModel):
    services: Mapping[str, str] = {}
    config: List[RTVIServiceConfig] = []
    prompt: Optional[str] = ""


class BotParams(BaseModel):
    conversation_id: str
    prompt_config: BotSystemPrompt = Field(default_factory=BotSystemPrompt)
    actions: List[RTVIMessage] = []
    bot_profile: Optional[str] = None
    attachments: List[str] = []


class BotCallbacks(BaseModel):
    on_call_state_updated: Callable[[str], Awaitable[None]]
    on_first_participant_joined: Callable[[Mapping[str, Any]], Awaitable[None]]
    on_participant_joined: Callable[[Mapping[str, Any]], Awaitable[None]]
    on_participant_left: Callable[[Mapping[str, Any], str], Awaitable[None]]
