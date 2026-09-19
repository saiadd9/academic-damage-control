# Academic Damage Control Backend

Deterministic FastAPI backend foundation for Academic Damage Control.

## Structure

```text
backend/
  app/
    main.py              # FastAPI app setup
    routes.py            # HTTP endpoint definitions
    schemas.py           # Pydantic request/response models
    services/
      common.py          # Shared deterministic scoring helpers
      screwed_score.py   # How Screwed Am I? logic
      recovery.py        # I'll Do It Later planning logic
      damage_control.py  # Academic Damage Control triage logic
  tests/
    test_services.py     # Lightweight service tests without TestClient
  requirements.txt
```

## Run Locally

From `backend/`:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Then visit:

```text
http://127.0.0.1:8000/health
```

## Endpoints

- `GET /health`
- `POST /api/v1/screwed-score`
- `POST /api/v1/recovery-plan`
- `POST /api/v1/damage-control`

## Example Task Shape

```json
{
  "title": "History essay",
  "deadline": "2026-09-26T12:00:00",
  "progress_percent": 45,
  "estimated_hours_remaining": 8,
  "difficulty": 3,
  "grade_weight_percent": 25,
  "can_submit_partial": true
}
```

## Example Requests

### Screwed Score

```json
{
  "as_of": "2026-09-19T20:00:00",
  "available_study_hours": 10,
  "competing_workload_hours": 4,
  "tasks": [
    {
      "title": "Calculus problem set",
      "deadline": "2026-09-21T23:59:00",
      "progress_percent": 20,
      "estimated_hours_remaining": 6,
      "difficulty": 4,
      "grade_weight_percent": 12
    }
  ]
}
```

### Recovery Plan

```json
{
  "as_of": "2026-09-19T20:00:00",
  "available_windows": [
    {"date": "2026-09-20", "hours": 4},
    {"date": "2026-09-21", "hours": 5}
  ],
  "tasks": [
    {
      "title": "History essay",
      "deadline": "2026-09-26T12:00:00",
      "progress_percent": 45,
      "estimated_hours_remaining": 8,
      "difficulty": 3,
      "grade_weight_percent": 25
    }
  ]
}
```

### Damage Control

```json
{
  "as_of": "2026-09-19T20:00:00",
  "available_hours": 7,
  "tasks": [
    {
      "title": "History essay",
      "deadline": "2026-09-26T12:00:00",
      "progress_percent": 45,
      "estimated_hours_remaining": 8,
      "difficulty": 3,
      "grade_weight_percent": 25
    }
  ]
}
```

## This Milestone Implements

- Deterministic scoring for "How Screwed Am I?"
- Deterministic recovery planning for "I'll Do It Later"
- Deterministic triage for "Academic Damage Control"
- Pydantic validation for task fields, percentages, hours, and difficulty
- Service-layer logic separated from API route handlers
- Lightweight automated tests that avoid the current FastAPI TestClient/httpx2 issue

## Intentionally Postponed

- Google ADK/Gemini
- Supabase persistence
- Authentication
- User history or memory
- Procrastination/optimism multipliers
- Panic Mode
- Frontend integration
