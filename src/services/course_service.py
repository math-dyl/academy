from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .content_service import ContentService


@dataclass(slots=True)
class Topic:
    course: str
    topic: str
    path: Path

    files: list[str] = field(
        default_factory=list
    )


class CourseService:
    """
    Course structure:

    data/
        courses/
            <course>/
                <topic>/
                    course.json
                    lessons.json
                    practice.json
                    quizzes.json

    Lesson examples are optional and are stored
    directly inside lessons.json.
    """

    REQUIRED_FILES = {
        "course.json",
        "lessons.json",
        "practice.json",
        "quizzes.json",
    }

    def __init__(
        self,
        content_service: ContentService,
        courses_dir: Path,
    ):
        self.content = content_service

        self.courses_dir = Path(
            courses_dir
        )

    # ==================================================
    # DISCOVERY
    # ==================================================

    def discover(self) -> list[Topic]:
        topics: list[Topic] = []

        if not self.courses_dir.exists():
            return topics

        for course_dir in sorted(
            self.courses_dir.iterdir()
        ):
            if not course_dir.is_dir():
                continue

            for topic_dir in sorted(
                course_dir.iterdir()
            ):
                if not topic_dir.is_dir():
                    continue

                course_json = (
                    topic_dir / "course.json"
                )

                if not course_json.is_file():
                    continue

                json_files = sorted(
                    path.name
                    for path in topic_dir.glob(
                        "*.json"
                    )
                    if path.is_file()
                )

                topics.append(
                    Topic(
                        course=course_dir.name,
                        topic=topic_dir.name,
                        path=topic_dir,
                        files=json_files,
                    )
                )

        return topics

    # ==================================================
    # COURSES
    # ==================================================

    def courses(self) -> list[str]:
        return sorted(
            {
                item.course
                for item in self.discover()
            }
        )

    # ==================================================
    # TOPICS
    # ==================================================

    def topics(
        self,
        course: str,
    ) -> list[Topic]:

        course = course.strip().lower()

        return [
            item
            for item in self.discover()
            if item.course.lower() == course
        ]

    # ==================================================
    # FIND TOPIC
    # ==================================================

    def get_topic(
        self,
        course: str,
        topic: str,
    ) -> Topic | None:

        course = course.strip().lower()
        topic = topic.strip().lower()

        for item in self.discover():
            if (
                item.course.lower() == course
                and item.topic.lower() == topic
            ):
                return item

        return None

    # ==================================================
    # LOAD TOPIC FILE
    # ==================================================

    def load_topic_file(
        self,
        course: str,
        topic: str,
        filename: str,
        default=None,
    ):
        topic_data = self.get_topic(
            course,
            topic,
        )

        if topic_data is None:
            return (
                {}
                if default is None
                else default
            )

        filename = Path(
            filename
        ).name

        path = (
            topic_data.path
            / filename
        )

        return self.content.load_json(
            path,
            default,
        )

    # ==================================================
    # COURSE CONFIG
    # ==================================================

    def course_config(
        self,
        course: str,
        topic: str,
    ) -> dict:

        data = self.load_topic_file(
            course,
            topic,
            "course.json",
            {},
        )

        return (
            data
            if isinstance(data, dict)
            else {}
        )

    # ==================================================
    # CHANNEL ID
    # ==================================================

    def channel_id(
        self,
        course: str,
        topic: str,
    ) -> int | None:

        config = self.course_config(
            course,
            topic,
        )

        value = config.get(
            "channel_id"
        )

        if value is None:
            return None

        try:
            return int(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

    # ==================================================
    # LESSONS
    # ==================================================

    def lessons(
        self,
        course: str,
        topic: str,
    ) -> list:

        data = self.load_topic_file(
            course,
            topic,
            "lessons.json",
            [],
        )

        return self._as_list(data)

    # ==================================================
    # PRACTICE
    # ==================================================

    def practice(
        self,
        course: str,
        topic: str,
    ) -> list:

        data = self.load_topic_file(
            course,
            topic,
            "practice.json",
            [],
        )

        return self._as_list(data)

    # ==================================================
    # QUIZZES
    # ==================================================

    def quizzes(
        self,
        course: str,
        topic: str,
    ) -> list:

        data = self.load_topic_file(
            course,
            topic,
            "quizzes.json",
            [],
        )

        return self._as_list(data)

    # ==================================================
    # INTERNAL
    # ==================================================

    @staticmethod
    def _as_list(data) -> list:

        if isinstance(data, list):
            return data

        if isinstance(data, dict):

            possible_keys = [
                "items",
                "data",
                "lessons",
                "practice",
                "questions",
                "quizzes",
            ]

            for key in possible_keys:

                value = data.get(key)

                if isinstance(
                    value,
                    list,
                ):
                    return value

        return []