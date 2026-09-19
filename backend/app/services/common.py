from datetime import datetime

from app.schemas import AcademicTask, Factor


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def rounded_hours(value: float) -> float:
    return round(max(0, value), 2)


def days_until(deadline: datetime, as_of: datetime) -> float:
    return round((deadline - as_of).total_seconds() / 86400, 2)


def deadline_pressure(days_left: float) -> float:
    if days_left <= 0:
        return 100
    if days_left <= 1:
        return 92
    if days_left <= 3:
        return 78
    if days_left <= 7:
        return 58
    if days_left <= 14:
        return 35
    return 15


def task_priority_score(task: AcademicTask, as_of: datetime) -> int:
    days_left = days_until(task.deadline, as_of)
    urgency = deadline_pressure(days_left)
    effort_pressure = clamp(task.estimated_hours_remaining * 8)
    progress_gap = 100 - task.progress_percent
    difficulty_pressure = task.difficulty * 20
    score = (
        urgency * 0.35
        + task.grade_weight_percent * 0.25
        + effort_pressure * 0.18
        + progress_gap * 0.12
        + difficulty_pressure * 0.10
    )
    return round(clamp(score))


def make_factor(name: str, score: float, weight: float, explanation: str) -> Factor:
    return Factor(
        name=name,
        score=round(clamp(score), 2),
        weight=weight,
        explanation=explanation,
    )
