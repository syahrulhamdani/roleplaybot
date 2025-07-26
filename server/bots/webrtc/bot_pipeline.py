from typing import Any, Dict, Optional

from loguru import logger
from openai._types import NOT_GIVEN
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import EndFrame, LLMMessagesFrame, TTSSpeakFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.processors.user_idle_processor import UserIdleProcessor
from pipecat.services.ai_services import OpenAILLMContext
from pipecat.services.gemini_multimodal_live.gemini import (
    GeminiMultimodalLiveLLMService, InputParams
)
from pipecat.services.google.rtvi import RTVIObserver
from pipecat.transports.services.daily import DailyParams, DailyTransport
from sqlalchemy.ext.asyncio import AsyncSession

from bots.persistent_context import PersistentContext
from bots.rtvi import create_rtvi_processor
from bots.types import BotCallbacks, BotConfig, BotParams
from common.config import (
    ENV,
    PROMPT_NAME,
    SERVICE_API_KEYS,
    USE_CASE,
    ROLEPLAY_SCENARIO,
)
from common.config_models import ConfigListResponse
from common.models import Conversation, Message
from common.prompt_models import PromptResponse
from services import ConfigService, PromptService
from services.prompt_service import get_latest_prompt


async def _get_latest_config(
    use_case: str = USE_CASE, env: str = ENV
) -> Optional[ConfigListResponse]:
    """
    Fetch the latest configuration from ConfigService.

    Args:
        use_case: The use case for the configuration
        env: Environment (e.g., dev, staging, prod)

    Returns:
        The latest configuration if found, None otherwise
    """
    async with ConfigService() as config_service:
        try:
            configs = await config_service.list_configs(
                env=env, useCase=use_case, size=10
            )
            return configs
        except Exception as e:
            logger.error(f"Error fetching config: {e}")
    return None


async def bot_pipeline(
    params: BotParams,
    config: BotConfig,
    callbacks: BotCallbacks,
    room_url: str,
    room_token: str,
    db: AsyncSession,
) -> (Pipeline, RTVIObserver):
    # Get latest config and prompt
    async with PromptService() as prompt_service:
        latest_prompt = await get_latest_prompt(
            service=prompt_service, prompt_name=PROMPT_NAME, use_case=USE_CASE, env=ENV
        )
    latest_config = await _get_latest_config()

    # Update config with latest values if available
    logger.debug("Initiating DailyTransport")
    transport = DailyTransport(
        room_url,
        room_token,
        "Gemini Bot",
        DailyParams(
            audio_in_sample_rate=16000,
            audio_in_enabled=True,
            audio_out_enabled=True,
            audio_out_sample_rate=24000,
            transcription_enabled=False,  # We're using Gemini for transcription
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(
                params=VADParams(
                    confidence=.85,
                    stop_secs=5,
                    start_secs=.5,
                )
            ),
            vad_audio_passthrough=True,
        ),
    )
    logger.debug("Initiated DailyTransport")

    logger.debug("Fetching conversations")
    conversation = await Conversation.get_conversation_by_id(params.conversation_id, db)
    if not conversation:
        raise Exception(f"Conversation {params.conversation_id} not found")
    messages = [getattr(msg, "content") for msg in conversation.messages]
    logger.debug("Got %d messages", len(messages))

    if not params.prompt_config.language:
        params.prompt_config.language = next(
            c.value for c in latest_config.items if c.name == "voice_language"
        )
        logger.warning(
            "Prompt language not set. Using latest config: {}",
            params.prompt_config.language,
        )

    if not params.prompt_config.scenario:
        logger.warning("Prompt scenario not set. Using default scenario")
        async with PromptService() as prompt_service:
            scenario_prompt = await get_latest_prompt(
                service=prompt_service,
                prompt_name=ROLEPLAY_SCENARIO,
                use_case=USE_CASE,
                env=ENV,
            )
            params.prompt_config.scenario = (
                scenario_prompt.content if scenario_prompt else ""
            )

    try:
        logger.debug("Initiating GeminiMultimodalLiveLLMService")
        system_prompt = latest_prompt.content.format(
            **params.prompt_config.model_dump()
        )
        llm_rt = GeminiMultimodalLiveLLMService(
            model="models/gemini-2.5-flash-preview-native-audio-dialog",
            api_key=str(SERVICE_API_KEYS["gemini"]),
            voice_id=[
                config.value
                for config in latest_config.items
                if config.name == "voice_id"
            ][0],
            system_instruction=system_prompt,
            transcribe_user_audio=True,
            transcribe_model_audio=True,
            inference_on_context_initialization=False,
        )
    except Exception as e:
        logger.error(f"Failed to initialize GeminiMultimodalLiveLLMService: {str(e)}")
        raise

    logger.debug(f"Initiated GeminiMultimodalLiveLLMService")
    tools = NOT_GIVEN  # todo: implement tools in and set here
    context_rt = OpenAILLMContext(messages, tools)
    context_aggregator_rt = llm_rt.create_context_aggregator(context_rt)
    user_aggregator = context_aggregator_rt.user()
    assistant_aggregator = context_aggregator_rt.assistant()
    await llm_rt.set_context(context_rt)
    storage = PersistentContext(context=context_rt)

    async def handle_idle(user_idle: UserIdleProcessor, retry_count: int):
        if retry_count == 1:
            messages.append(
                {
                    "role": "system",
                    "content": "The user has been quiet. Politely and briefly ask if they're still there.",
                }
            )
            await user_idle.push_frame(LLMMessagesFrame(messages))
            return True

        if retry_count == 2:
            messages.append(
                {
                    "role": "system",
                    "content": "The user is still inactive. Ask if they'd like to continue our conversation.",
                }
            )
            await user_idle.push_frame(LLMMessagesFrame(messages))
            return True

        await user_idle.push_frame(
            TTSSpeakFrame(
                text="Jika tidak ada yang ingin Anda bicarakan, kita bisa menutup percakapan ini."
            )
        )
        return False

    @storage.on_context_message
    async def on_context_message(messages: list[Any]):
        logger.debug(f"{len(messages)} message(s) received for storage")
        try:
            await Message.create_messages(
                db_session=db, conversation_id=params.conversation_id, messages=messages
            )
        except Exception as e:
            logger.error(f"Error storing messages: {e}")
            raise e

    # Create RTVI processor with transcription enabled
    rtvi = await create_rtvi_processor(config, user_aggregator)

    user_idle = UserIdleProcessor(
        callback=handle_idle,
        timeout=5.0,
    )

    logger.debug("Initiating processors")
    processors = [
        transport.input(),
        rtvi,
        user_aggregator,
        llm_rt,
        transport.output(),
        assistant_aggregator,
        storage.create_processor(exit_on_endframe=True),
    ]

    # Create and register the RTVI observer for handling RTVI events
    rtvi_observer = RTVIObserver(rtvi=rtvi)

    # No need to configure Daily's transcription as we're using Gemini
    # The RTVI observer will automatically handle transcription events through the RTVI processor

    pipeline = Pipeline(processors)
    logger.debug("Initiated pipeline")

    @rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        await rtvi.set_bot_ready()
        for message in params.actions:
            await rtvi.handle_message(message)

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        # Enable both camera and screenshare. From the client side
        # send just one.
        await transport.capture_participant_video(
            participant["id"], framerate=1, video_source="camera"
        )
        await transport.capture_participant_video(
            participant["id"], framerate=1, video_source="screenVideo"
        )
        await callbacks.on_first_participant_joined(participant)

    @transport.event_handler("on_participant_joined")
    async def on_participant_joined(transport, participant):
        await callbacks.on_participant_joined(participant)

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        await callbacks.on_participant_left(participant, reason)

    @transport.event_handler("on_call_state_updated")
    async def on_call_state_updated(transport, state):
        await callbacks.on_call_state_updated(state)

    return pipeline, rtvi_observer
