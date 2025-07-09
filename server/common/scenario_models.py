"""Data model for scenario agent."""

from pydantic import BaseModel, Field


class ScenarioState(BaseModel):
    level: str = Field(description="Level of the scenario")
    topic: str = Field(description="Topic of the scenario")
    other_instructions: str | None = Field(
        default="", description="Other instructions for the scenario"
    )


class ScenarioInputPayload(ScenarioState):
    pass


class ScenarioMetric(BaseModel):
    metric: str = Field(description="Metric / evaluation criteria for the scenario")
    description: str = Field(description="Description of the metric")
    min_score: float = Field(description="Minimum score range for the metric")
    max_score: float = Field(description="Maximum score range for the metric")


class ScenarioDetail(BaseModel):
    scenario: str = Field(
        description=(
            "A descriptive scenario based on given level, topic, and other instructions"
            " in markdown format"
        )
    )
    metrics: list[ScenarioMetric]


class ScenarioResponse(BaseModel):
    response: ScenarioDetail
