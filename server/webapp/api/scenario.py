"""Endpoints for scenario generation."""

from time import time

from fastapi import APIRouter, status, HTTPException
from loguru import logger

from bots.scenario_agent import ScenarioAgent
from common.config import SCENARIO_PROMPT_NAME
from common.scenario_models import ScenarioInputPayload, ScenarioDetail

service = ScenarioAgent(prompt_name=SCENARIO_PROMPT_NAME)
router = APIRouter(prefix="/scenarios")


@router.post("", response_model=ScenarioDetail)
async def generate_scenario(payload: ScenarioInputPayload):
    t0 = time()
    try:
        response = await service.agent.ainvoke(payload.model_dump())
    except Exception as exc:
        logger.exception("Failed to generate scenario: {}", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate scenario: {exc}",
        )
    return ScenarioDetail.model_validate(response["response"])
