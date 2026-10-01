from __future__ import annotations


class LearningProgress:

    def __init__(self):
        self._progress = {}

    # ==================================================
    # GET PROGRESS
    # ==================================================

    def get(
        self,
        user_id: int,
        course: str,
        topic: str,
    ) -> int:

        key = (user_id, course, topic)

        return self._progress.get(
            key,
            0,
        )

    # ==================================================
    # SAVE PROGRESS
    # ==================================================

    def save(
        self,
        user_id: int,
        course: str,
        topic: str,
        lesson_index: int,
    ):

        key = (user_id, course, topic)

        self._progress[key] = lesson_index

    # ==================================================
    # CLEAR PROGRESS
    # ==================================================

    def clear(
        self,
        user_id: int,
        course: str,
        topic: str,
    ):

        key = (user_id, course, topic)

        self._progress.pop(
            key,
            None,
        )