from __future__ import annotations

import random


class PracticeService:

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

        return self.course_service.practice(
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