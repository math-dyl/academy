from __future__ import annotations

import random


class QuizService:

    def __init__(
        self,
        course_service,
    ):

        self.course_service = (
            course_service
        )

    # ==================================================
    # QUESTIONS
    # ==================================================

    def questions(
        self,
        course: str,
        topic: str,
    ) -> list[dict]:

        return self.course_service.quizzes(
            course,
            topic,
        )

    # ==================================================
    # RANDOM QUESTION
    # ==================================================

    def random_question(
        self,
        course: str,
        topic: str,
    ):

        questions = self.questions(
            course,
            topic,
        )

        if not questions:
            return None

        return random.choice(
            questions
        )

    # ==================================================
    # CHECK ANSWER
    # ==================================================

    @staticmethod
    def check(
        question: dict,
        answer: str,
    ) -> bool:

        expected = question.get(
            "answer",
            question.get(
                "correct_answer"
            ),
        )

        if expected is None:
            return False

        if isinstance(
            expected,
            list,
        ):

            return (
                answer.strip().lower()
                in {
                    str(item)
                    .strip()
                    .lower()
                    for item in expected
                }
            )

        return (
            answer.strip().lower()
            == str(expected)
            .strip()
            .lower()
        )