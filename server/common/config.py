import os

from bots.types import BotConfig


def to_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "y", "yes")


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_USE_BASIC_FORMAT = to_bool(os.getenv("LOG_USE_BASIC_FORMAT", "False"))
ENABLE_CLOUD_LOGGING = to_bool(os.getenv("ENABLE_CLOUD_LOGGING", "False"))

DEFAULT_LLM_CONTEXT = []
DEFAULT_BOT_CONFIG = BotConfig(
    config=[
        {
            "options": [{"name": "params", "value": {"stop_secs": 0.5}}],
            "service": "vad",
        },
        {
            "options": [
                {"name": "run_on_config", "value": False},
            ],
            "service": "llm",
        },
    ],
)

SERVICE_API_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY"),
    "daily": os.getenv("DAILY_API_KEY"),
}

ENV = os.getenv("ENV", "dev")
USE_CASE = os.getenv("USE_CASE", "voice-agent")
PROMPT_NAME = os.getenv("PROMPT_NAME", "voice_agent_prompt")
SCENARIO_PROMPT_NAME = os.getenv(
    "SCENARIO_PROMPT_NAME", "roleplay_scenario_generator_prompt"
)
ROLEPLAY_SCENARIO = os.getenv("ROLEPLAY_SCENARIO", "default_roleplay_scenario")
