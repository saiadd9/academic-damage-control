from fastapi import APIRouter

from app.schemas import (
    DamageControlRequest,
    DamageControlResponse,
    HealthResponse,
    RecoveryPlanRequest,
    RecoveryPlanResponse,
    ScrewedScoreRequest,
    ScrewedScoreResponse,
)
from app.services.damage_control import create_damage_control_plan
from app.services.recovery import create_recovery_plan
from app.services.screwed_score import analyze_screwed_score


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/api/v1/screwed-score", response_model=ScrewedScoreResponse)
def screwed_score(request: ScrewedScoreRequest) -> ScrewedScoreResponse:
    return analyze_screwed_score(request)


@router.post("/api/v1/recovery-plan", response_model=RecoveryPlanResponse)
def recovery_plan(request: RecoveryPlanRequest) -> RecoveryPlanResponse:
    return create_recovery_plan(request)


@router.post("/api/v1/damage-control", response_model=DamageControlResponse)
def damage_control(request: DamageControlRequest) -> DamageControlResponse:
    return create_damage_control_plan(request)
