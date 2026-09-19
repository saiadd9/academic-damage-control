from app.schemas import (
    PlannedSession,
    PrioritizedTask,
    RecoveryPlanRequest,
    RecoveryPlanResponse,
    UnscheduledTask,
)
from app.services.common import rounded_hours, task_priority_score


def create_recovery_plan(request: RecoveryPlanRequest) -> RecoveryPlanResponse:
    ranked_tasks = sorted(
        request.tasks,
        key=lambda task: task_priority_score(task, request.as_of),
        reverse=True,
    )
    remaining_by_title = {
        task.title: rounded_hours(task.estimated_hours_remaining) for task in ranked_tasks
    }
    sessions: list[PlannedSession] = []

    for window in sorted(request.available_windows, key=lambda item: item.date):
        hours_left = rounded_hours(window.hours)
        for task in ranked_tasks:
            if hours_left <= 0:
                break
            remaining = remaining_by_title[task.title]
            if remaining <= 0:
                continue
            chunk = min(remaining, hours_left, 2.0)
            sessions.append(
                PlannedSession(
                    date=window.date,
                    task_title=task.title,
                    hours=rounded_hours(chunk),
                    focus=_session_focus(task.progress_percent, remaining),
                )
            )
            remaining_by_title[task.title] = rounded_hours(remaining - chunk)
            hours_left = rounded_hours(hours_left - chunk)

    prioritized = [
        PrioritizedTask(
            title=task.title,
            priority_score=task_priority_score(task, request.as_of),
            reason=_priority_reason(task, request.as_of),
            estimated_hours_remaining=rounded_hours(task.estimated_hours_remaining),
        )
        for task in ranked_tasks
    ]
    unscheduled = [
        UnscheduledTask(
            title=task.title,
            hours_unplanned=hours_left,
            reason="Not enough available study time after higher-priority work was scheduled.",
        )
        for task in ranked_tasks
        if (hours_left := remaining_by_title[task.title]) > 0
    ]
    total_available = rounded_hours(sum(window.hours for window in request.available_windows))
    total_required = rounded_hours(sum(task.estimated_hours_remaining for task in request.tasks))

    if unscheduled:
        summary = "Plan covers the highest-priority work first, but some hours remain unscheduled."
    else:
        summary = "Plan fits all listed work into the available study windows."

    return RecoveryPlanResponse(
        total_available_hours=total_available,
        total_required_hours=total_required,
        prioritized_tasks=prioritized,
        sessions=sessions,
        unscheduled_tasks=unscheduled,
        summary=summary,
    )


def _priority_reason(task, as_of) -> str:
    score = task_priority_score(task, as_of)
    return (
        f"Priority {score}/100 based on deadline proximity, {task.grade_weight_percent:.1f}% grade weight, "
        f"{task.estimated_hours_remaining:.1f} hours remaining, {task.progress_percent}% progress, "
        f"and difficulty {task.difficulty}/5."
    )


def _session_focus(progress_percent: int, remaining_hours: float) -> str:
    if progress_percent < 25:
        return "Create outline and complete the first concrete deliverable."
    if remaining_hours <= 2:
        return "Finish, polish, and prepare submission."
    return "Make measurable progress on the highest-value remaining section."
