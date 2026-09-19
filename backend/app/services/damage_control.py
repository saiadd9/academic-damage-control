from app.schemas import DamageControlItem, DamageControlRequest, DamageControlResponse
from app.services.common import days_until, rounded_hours, task_priority_score


def create_damage_control_plan(request: DamageControlRequest) -> DamageControlResponse:
    ranked_tasks = sorted(
        request.tasks,
        key=lambda task: task_priority_score(task, request.as_of),
        reverse=True,
    )
    remaining_capacity = request.available_hours
    items: list[DamageControlItem] = []

    for task in ranked_tasks:
        priority = task_priority_score(task, request.as_of)
        days_left = days_until(task.deadline, request.as_of)
        full_hours = task.estimated_hours_remaining

        if remaining_capacity >= full_hours and priority >= 50:
            action = "protect"
            recommended = full_hours
            rationale = "High enough value and feasible within remaining time; protect full completion."
        elif remaining_capacity > 0 and (priority >= 55 or task.grade_weight_percent >= 20):
            action = "reduce"
            target = full_hours * (0.65 if task.can_submit_partial else 0.4)
            recommended = min(remaining_capacity, target)
            rationale = "Important work, but full completion may crowd out other deadlines; aim for the highest-yield subset."
        elif days_left > 7 and task.grade_weight_percent < 25:
            action = "defer"
            recommended = 0
            rationale = "Lower immediate urgency; revisit after the near-term damage is contained."
        else:
            action = "deprioritize"
            recommended = 0
            rationale = "Low feasibility or lower grade impact compared with more urgent work."

        recommended = rounded_hours(recommended)
        remaining_capacity = rounded_hours(remaining_capacity - recommended)
        items.append(
            DamageControlItem(
                title=task.title,
                action=action,
                recommended_hours=recommended,
                rationale=rationale,
                priority_score=priority,
            )
        )

    protected_hours = rounded_hours(
        sum(item.recommended_hours for item in items if item.action in {"protect", "reduce"})
    )
    total_required = rounded_hours(sum(task.estimated_hours_remaining for task in request.tasks))
    summary = (
        "Capacity is below required effort, so the plan protects high-impact work and limits low-yield work."
        if request.available_hours < total_required
        else "Available time can cover the listed work; protect high-priority completion first."
    )
    return DamageControlResponse(
        total_available_hours=rounded_hours(request.available_hours),
        total_required_hours=total_required,
        protected_hours=protected_hours,
        items=items,
        summary=summary,
    )
