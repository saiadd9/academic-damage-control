from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class HealthResponse(BaseModel):
    status: str


class AcademicTask(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    deadline: datetime
    progress_percent: int = Field(..., ge=0, le=100)
    estimated_hours_remaining: float = Field(..., ge=0, le=500)
    difficulty: int = Field(..., ge=1, le=5)
    grade_weight_percent: float = Field(..., ge=0, le=100)
    can_submit_partial: bool = True

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be blank")
        return value


class StudyWindow(BaseModel):
    date: date
    hours: float = Field(..., ge=0, le=24)


class Factor(BaseModel):
    name: str
    score: float = Field(..., ge=0, le=100)
    weight: float = Field(..., ge=0, le=1)
    explanation: str


class TaskRisk(BaseModel):
    title: str
    risk_score: int = Field(..., ge=0, le=100)
    days_until_deadline: float
    factors: list[Factor]


class ScrewedScoreRequest(BaseModel):
    as_of: datetime
    available_study_hours: float = Field(..., ge=0, le=500)
    competing_workload_hours: float = Field(0, ge=0, le=500)
    tasks: list[AcademicTask] = Field(..., min_length=1, max_length=50)


class ScrewedScoreResponse(BaseModel):
    screwed_score: int = Field(..., ge=0, le=100)
    severity: Literal["low", "guarded", "serious", "critical"]
    summary: str
    overall_factors: list[Factor]
    task_risks: list[TaskRisk]


class RecoveryPlanRequest(BaseModel):
    as_of: datetime
    available_windows: list[StudyWindow] = Field(..., min_length=1, max_length=30)
    tasks: list[AcademicTask] = Field(..., min_length=1, max_length=50)

    @model_validator(mode="after")
    def ensure_some_time(self) -> "RecoveryPlanRequest":
        if sum(window.hours for window in self.available_windows) <= 0:
            raise ValueError("available_windows must include at least some study time")
        return self


class PrioritizedTask(BaseModel):
    title: str
    priority_score: int = Field(..., ge=0, le=100)
    reason: str
    estimated_hours_remaining: float


class PlannedSession(BaseModel):
    date: date
    task_title: str
    hours: float = Field(..., ge=0)
    focus: str


class UnscheduledTask(BaseModel):
    title: str
    hours_unplanned: float = Field(..., ge=0)
    reason: str


class RecoveryPlanResponse(BaseModel):
    total_available_hours: float = Field(..., ge=0)
    total_required_hours: float = Field(..., ge=0)
    prioritized_tasks: list[PrioritizedTask]
    sessions: list[PlannedSession]
    unscheduled_tasks: list[UnscheduledTask]
    summary: str


class DamageControlRequest(BaseModel):
    as_of: datetime
    available_hours: float = Field(..., ge=0, le=500)
    tasks: list[AcademicTask] = Field(..., min_length=1, max_length=50)


class DamageControlItem(BaseModel):
    title: str
    action: Literal["protect", "reduce", "defer", "deprioritize"]
    recommended_hours: float = Field(..., ge=0)
    rationale: str
    priority_score: int = Field(..., ge=0, le=100)


class DamageControlResponse(BaseModel):
    total_available_hours: float = Field(..., ge=0)
    total_required_hours: float = Field(..., ge=0)
    protected_hours: float = Field(..., ge=0)
    items: list[DamageControlItem]
    summary: str
