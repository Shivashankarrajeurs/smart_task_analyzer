from django.test import TestCase
from .scoring import score_tasks, detect_cycles
from datetime import datetime, timedelta

class ScoringTests(TestCase):

    def setUp(self):
        today = datetime.now().date()
        self.task_soon = {
            "title": "Soon",
            "due_date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            "estimated_hours": 2,
            "importance": 7,
            "dependencies": []
        }
        self.task_overdue = {
            "title": "Overdue",
            "due_date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
            "estimated_hours": 5,
            "importance": 6,
            "dependencies": []
        }
        self.task_quick = {
            "title": "Quick",
            "due_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "estimated_hours": 0.5,
            "importance": 5,
            "dependencies": []
        }

    def test_score_ordering(self):
        scored = score_tasks([self.task_quick, self.task_overdue, self.task_soon])
        self.assertEqual(len(scored), 3)
        self.assertIn("score", scored[0])
        self.assertIn("explanation", scored[0])

    def test_detect_cycle_raises(self):
        tasks = {
            0: {"dependencies": [1]},
            1: {"dependencies": [0]},
        }
        with self.assertRaises(ValueError):
            detect_cycles(tasks)

    def test_no_cycle_passes(self):
        tasks = {
            0: {"dependencies": [1]},
            1: {"dependencies": []},
            2: {"dependencies": [1]},
        }
        detect_cycles(tasks)
