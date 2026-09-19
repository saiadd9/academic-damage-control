import unittest

from app.routes import health
from app.schemas import DamageControlRequest, RecoveryPlanRequest, ScrewedScoreRequest
from app.services.damage_control import create_damage_control_plan
from app.services.recovery import create_recovery_plan
from app.services.screwed_score import analyze_screwed_score


TASKS = [
    {
        "title": "Calculus problem set",
        "deadline": "2026-09-21T23:59:00",
        "progress_percent": 20,
        "estimated_hours_remaining": 6,
        "difficulty": 4,
        "grade_weight_percent": 12,
    },
    {
        "title": "History essay",
        "deadline": "2026-09-26T12:00:00",
        "progress_percent": 45,
        "estimated_hours_remaining": 8,
        "difficulty": 3,
        "grade_weight_percent": 25,
    },
]


class BackendServiceTests(unittest.TestCase):
    def test_health(self):
        self.assertEqual(health().model_dump(), {"status": "ok"})

    def test_screwed_score(self):
        response = analyze_screwed_score(
            ScrewedScoreRequest(
                as_of="2026-09-19T20:00:00",
                available_study_hours=10,
                competing_workload_hours=4,
                tasks=TASKS,
            )
        )
        self.assertGreaterEqual(response.screwed_score, 0)
        self.assertLessEqual(response.screwed_score, 100)
        self.assertEqual(len(response.task_risks), 2)

    def test_recovery_plan(self):
        response = create_recovery_plan(
            RecoveryPlanRequest(
                as_of="2026-09-19T20:00:00",
                available_windows=[
                    {"date": "2026-09-20", "hours": 4},
                    {"date": "2026-09-21", "hours": 5},
                ],
                tasks=TASKS,
            )
        )
        self.assertGreater(len(response.sessions), 0)
        self.assertEqual(response.total_available_hours, 9)

    def test_damage_control(self):
        response = create_damage_control_plan(
            DamageControlRequest(
                as_of="2026-09-19T20:00:00",
                available_hours=7,
                tasks=TASKS,
            )
        )
        self.assertEqual(len(response.items), 2)
        self.assertLessEqual(response.protected_hours, 7)


if __name__ == "__main__":
    unittest.main()
