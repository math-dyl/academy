from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
COURSES_DIR = DATA_DIR / "courses"


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Mathdyl Academy API",
    description="Backend API for Mathdyl Academy.",
    version="1.0.0",
)


# ============================================================
# HELPERS
# ============================================================

def load_json(path: Path, default=None):

    if not path.exists():

        return (
            {} if default is None else default
        )

    try:

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return (
            {} if default is None else default
        )


def topic_path(
    course: str,
    topic: str,
) -> Path:

    path = (
        COURSES_DIR
        / course
        / topic
    )

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Topic '{course}/{topic}' "
                "not found."
            ),
        )

    return path


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "Mathdyl Academy API",
        "version": "1.0.0",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():

    return {
        "status": "healthy",
        "service": "mathdyl-academy-api",
    }


# ============================================================
# COURSES
# ============================================================

@app.get("/api/courses")
def get_courses():

    if not COURSES_DIR.exists():

        return {
            "courses": []
        }

    courses = []

    for course_dir in sorted(
        COURSES_DIR.iterdir()
    ):

        if course_dir.is_dir():

            courses.append(
                course_dir.name
            )

    return {
        "courses": courses
    }


# ============================================================
# TOPICS
# ============================================================

@app.get(
    "/api/courses/{course}/topics"
)
def get_topics(
    course: str,
):

    course_dir = (
        COURSES_DIR / course
    )

    if not course_dir.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                f"Course '{course}' "
                "not found."
            ),
        )

    topics = []

    for topic_dir in sorted(
        course_dir.iterdir()
    ):

        if not topic_dir.is_dir():
            continue

        if not (
            topic_dir / "course.json"
        ).exists():
            continue

        config = load_json(
            topic_dir / "course.json",
            {},
        )

        topics.append(
            {
                "slug": topic_dir.name,
                "title": config.get(
                    "title",
                    topic_dir.name
                    .replace("-", " ")
                    .title(),
                ),
                "description": config.get(
                    "description",
                    "",
                ),
            }
        )

    return {
        "course": course,
        "topics": topics,
    }


# ============================================================
# COURSE CONFIG
# ============================================================

@app.get(
    "/api/courses/{course}/{topic}"
)
def get_topic(
    course: str,
    topic: str,
):

    path = topic_path(
        course,
        topic,
    )

    return load_json(
        path / "course.json",
        {},
    )


# ============================================================
# LESSONS
# ============================================================

@app.get(
    "/api/courses/{course}/{topic}/lessons"
)
def get_lessons(
    course: str,
    topic: str,
):

    path = topic_path(
        course,
        topic,
    )

    return {
        "course": course,
        "topic": topic,
        "lessons": load_json(
            path / "lessons.json",
            [],
        ),
    }


# ============================================================
# PRACTICE
# ============================================================

@app.get(
    "/api/courses/{course}/{topic}/practice"
)
def get_practice(
    course: str,
    topic: str,
):

    path = topic_path(
        course,
        topic,
    )

    return {
        "course": course,
        "topic": topic,
        "practice": load_json(
            path / "practice.json",
            [],
        ),
    }


# ============================================================
# QUIZZES
# ============================================================

@app.get(
    "/api/courses/{course}/{topic}/quizzes"
)
def get_quizzes(
    course: str,
    topic: str,
):

    path = topic_path(
        course,
        topic,
    )

    return {
        "course": course,
        "topic": topic,
        "quizzes": load_json(
            path / "quizzes.json",
            [],
        ),
    }