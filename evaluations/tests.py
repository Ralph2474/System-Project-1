from django.test import TestCase

from .models import EvaluationRecord


class EvaluationGradeTests(TestCase):
    def test_grade_and_percentage_are_calculated_from_all_scores(self):
        evaluation = EvaluationRecord(
            rating=5,
            punctuality=4,
            professionalism=5,
            teamwork=4,
        )

        self.assertEqual(evaluation.average_score, 4.5)
        self.assertEqual(evaluation.score_percent, 90)
        self.assertEqual(evaluation.grade, 'A')
