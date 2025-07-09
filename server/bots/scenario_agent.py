"""Agent related to scenario generation."""

from dataclasses import dataclass, field
from operator import add
from time import perf_counter

import mlflow.langchain
from loguru import logger
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate, BaseChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import START, END, MessagesState, StateGraph
from pydantic import BaseModel, Field

from common.scenario_models import ScenarioState, ScenarioResponse, ScenarioDetail
from services.prompt_service import PromptService, get_latest_prompt

mlflow.langchain.autolog()


@dataclass
class ScenarioAgent:
    """Agent for scenario generation."""

    llm: BaseLanguageModel = field(
        default_factory=lambda: ChatVertexAI(
            model_name="gemini-2.0-flash-001",
            temperature=0.5,
            top_p=0.4,
            max_tokens=1024,
        )
    )
    prompt_template: BaseChatPromptTemplate = None
    prompt_name: str = "scenario_agent_prompt"

    def __post_init__(self):
        if not self.prompt_template and not self.prompt_name:
            raise ValueError("prompt_template or prompt_name must be provided")

        self.graph = StateGraph(
            ScenarioState,
            output_schema=ScenarioResponse,
        )
        self.graph.add_node("generate_scenario", self.generate_scenario)
        self.graph.add_edge(START, "generate_scenario")
        self.graph.add_edge("generate_scenario", END)
        self.agent = self.graph.compile()

    async def get_prompt(self, prompt_name: str):
        async with PromptService() as service:
            return await get_latest_prompt(service, prompt_name)

    async def generate_scenario(self, state: ScenarioState) -> ScenarioResponse:
        logger.info("Start generating scenario")
        start = perf_counter()

        message = await self.get_prompt(self.prompt_name)
        message = message.content.format(**state.model_dump())
        generator = self.llm.with_structured_output(ScenarioDetail)
        scenario: ScenarioDetail = await generator.ainvoke([("user", message)])

        logger.info("Done generating scenario in {:.2f}s", perf_counter() - start)
        return {"response": scenario}
