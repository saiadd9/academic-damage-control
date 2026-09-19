from app.schemas import Factor, ScrewedScoreRequest, ScrewedScoreResponse, TaskRisk
from app.services.common import clamp, days_until, deadline_pressure, make_factor


def analyze_screwed_score(request: ScrewedScoreRequest) -> ScrewedScoreResponse:
    total_remaining = sum(task.estimated_hours_remaining for task in request.tasks)
    capacity = request.available_study_hours
    workload_ratio = total_remaining / max(capacity, 1)
    workload_pressure = clamp(workload_ratio * 70)
    competing_pressure = clamp(
        request.competing_workload_hours / max(capacity + request.competing_workload_hours, 1) * 100
    )

    task_risks = [_score_task(task, request.as_of, capacity) for task in request.tasks]
    average_task_risk = sum(task.risk_score for task in task_risks) / len(task_risks)
    highest_task_risk = max(task.risk_score for task in task_risks)

    overall_factors = [
        make_factor(
            "workload pressure",
            workload_pressure,
            0.30,
            f"{total_remaining:.1f} hours remain against {capacity:.1f} available hours.",
        ),
        make_factor(
            "highest single-task risk",
            highest_task_risk,
            0.30,
            "One very dangerous task can make the whole situation fragile.",
        ),
        make_factor(
            "average task risk",
            average_task_risk,
            0.25,
            "Measures whether risk is isolated or spread across the workload.",
        ),
        make_factor(
            "competing workload",
            competing_pressure,
            0.15,
            f"{request.competing_workload_hours:.1f} hours of other workload competes for attention.",
        ),
    ]
    score = round(sum(factor.score * factor.weight for factor in overall_factors))
    severity = _severity(score)

    return ScrewedScoreResponse(
        screwed_score=score,
        severity=severity,
        summary=_summary(score, severity),
        overall_factors=overall_factors,
        task_risks=task_risks,
    )


def _score_task(task, as_of, available_hours: float) -> TaskRisk:
    days_left = days_until(task.deadline, as_of)
    urgency = deadline_pressure(days_left)
    progress_gap = 100 - task.progress_percent
    effort_pressure = clamp(task.estimated_hours_remaining / max(available_hours, 1) * 100)
    difficulty_pressure = task.difficulty * 20
    grade_pressure = task.grade_weight_percent

    factors: list[Factor] = [
        make_factor("deadline pressure", urgency, 0.35, f"Deadline is in {days_left:.2f} days."),
        make_factor("progress gap", progress_gap, 0.20, f"{task.progress_percent}% complete."),
        make_factor(
            "remaining effort",
            effort_pressure,
            0.20,
            f"{task.estimated_hours_remaining:.1f} hours remain compared with available time.",
        ),
        make_factor("difficulty", difficulty_pressure, 0.10, f"Difficulty is {task.difficulty}/5."),
        make_factor("grade impact", grade_pressure, 0.15, f"Worth {task.grade_weight_percent:.1f}% of the grade."),
    ]
    risk_score = round(sum(factor.score * factor.weight for factor in factors))
    return TaskRisk(
        title=task.title,
        risk_score=risk_score,
        days_until_deadline=days_left,
        factors=factors,
    )


def _severity(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "serious"
    if score >= 35:
        return "guarded"
    return "low"


def _summary(score: int, severity: str) -> str:
    if severity == "critical":
        return f"Score {score}: triage is needed because time, deadlines, or workload are badly misaligned."
    if severity == "serious":
        return f"Score {score}: recovery is possible, but the highest-risk tasks need immediate attention."
    if severity == "guarded":
        return f"Score {score}: manageable if study time is protected and tasks are handled in priority order."
    return f"Score {score}: the situation is currently stable."
