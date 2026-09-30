from __future__ import annotations

import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import asyncpg


class DatabaseService:
    """
    PostgreSQL database service for the Mathdyl Discord Bot.

    Handles:
    - Discord users
    - AI daily usage limits
    - AI chat history
    - Quiz attempts
    - Individual quiz answers
    """

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL")

        if not self.database_url:
            raise RuntimeError(
                "DATABASE_URL environment variable is not set."
            )

        self.pool: asyncpg.Pool | None = None

    # ==========================================================
    # CONNECTION
    # ==========================================================

    async def connect(self) -> None:
        """Create the PostgreSQL connection pool."""

        if self.pool is not None:
            return

        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=1,
            max_size=5,
            command_timeout=30,
        )

    async def close(self) -> None:
        """Close the PostgreSQL connection pool."""

        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    def _get_pool(self) -> asyncpg.Pool:
        """Return the active connection pool."""

        if self.pool is None:
            raise RuntimeError(
                "Database pool is not initialized. "
                "Call await database.connect() first."
            )

        return self.pool

    # ==========================================================
    # USERS
    # ==========================================================

    async def upsert_user(
        self,
        user_id: int,
        username: str,
        display_name: str,
    ) -> None:
        """
        Create the user if they don't exist.

        If the user already exists, update their Discord information
        and last_seen timestamp.
        """

        pool = self._get_pool()

        await pool.execute(
            """
            INSERT INTO users (
                user_id,
                username,
                display_name,
                first_seen,
                last_seen
            )
            VALUES ($1, $2, $3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)

            ON CONFLICT (user_id)
            DO UPDATE SET
                username = EXCLUDED.username,
                display_name = EXCLUDED.display_name,
                last_seen = CURRENT_TIMESTAMP
            """,
            user_id,
            username,
            display_name,
        )

    async def get_user(
        self,
        user_id: int,
    ) -> dict[str, Any] | None:
        """Get a user by Discord ID."""

        pool = self._get_pool()

        row = await pool.fetchrow(
            """
            SELECT
                user_id,
                username,
                display_name,
                first_seen,
                last_seen
            FROM users
            WHERE user_id = $1
            """,
            user_id,
        )

        return dict(row) if row else None

    # ==========================================================
    # AI CHAT USAGE
    # ==========================================================

    async def get_ai_usage(
        self,
        user_id: int,
        usage_date: date | None = None,
    ) -> int:
        """
        Get the number of AI chats used by a user today.

        Returns 0 if no record exists.
        """

        pool = self._get_pool()

        if usage_date is None:
            usage_date = date.today()

        count = await pool.fetchval(
            """
            SELECT chat_count
            FROM ai_chat_usage
            WHERE user_id = $1
              AND usage_date = $2
            """,
            user_id,
            usage_date,
        )

        return int(count or 0)

    async def increment_ai_usage(
        self,
        user_id: int,
        usage_date: date | None = None,
    ) -> int:
        """
        Increment today's AI usage count.

        Returns the new usage count.
        """

        pool = self._get_pool()

        if usage_date is None:
            usage_date = date.today()

        count = await pool.fetchval(
            """
            INSERT INTO ai_chat_usage (
                user_id,
                usage_date,
                chat_count
            )
            VALUES ($1, $2, 1)

            ON CONFLICT (user_id, usage_date)
            DO UPDATE SET
                chat_count = ai_chat_usage.chat_count + 1

            RETURNING chat_count
            """,
            user_id,
            usage_date,
        )

        return int(count)

    async def can_use_ai(
        self,
        user_id: int,
        daily_limit: int = 3,
        usage_date: date | None = None,
    ) -> bool:
        """
        Check whether the user can still use /ask today.
        """

        usage = await self.get_ai_usage(
            user_id=user_id,
            usage_date=usage_date,
        )

        return usage < daily_limit

    # ==========================================================
    # AI CHAT HISTORY
    # ==========================================================

    async def save_ai_chat(
        self,
        user_id: int,
        user_message: str,
        ai_response: str,
        model: str | None = None,
    ) -> int:
        """
        Save an AI conversation.

        Returns the inserted message ID.
        """

        pool = self._get_pool()

        message_id = await pool.fetchval(
            """
            INSERT INTO ai_chat_messages (
                user_id,
                user_message,
                ai_response,
                model
            )
            VALUES ($1, $2, $3, $4)

            RETURNING id
            """,
            user_id,
            user_message,
            ai_response,
            model,
        )

        return int(message_id)

    async def get_recent_ai_chats(
        self,
        user_id: int,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Get recent AI conversations for a user.
        """

        pool = self._get_pool()

        rows = await pool.fetch(
            """
            SELECT
                id,
                user_message,
                ai_response,
                model,
                created_at
            FROM ai_chat_messages
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            user_id,
            limit,
        )

        return [dict(row) for row in rows]

    # ==========================================================
    # QUIZ ATTEMPTS
    # ==========================================================

    async def create_quiz_attempt(
        self,
        user_id: int,
        course: str,
        topic: str,
        score: int,
        total_items: int,
    ) -> int:
        """
        Save a completed quiz attempt.

        Returns the generated attempt ID.
        """

        pool = self._get_pool()

        if total_items <= 0:
            raise ValueError("total_items must be greater than 0.")

        if score < 0 or score > total_items:
            raise ValueError(
                "score must be between 0 and total_items."
            )

        percentage = (score / total_items) * 100

        attempt_id = await pool.fetchval(
            """
            INSERT INTO quiz_attempts (
                user_id,
                course,
                topic,
                score,
                total_items,
                percentage
            )
            VALUES ($1, $2, $3, $4, $5, $6)

            RETURNING id
            """,
            user_id,
            course,
            topic,
            score,
            total_items,
            percentage,
        )

        return int(attempt_id)

    async def get_quiz_attempt(
        self,
        attempt_id: int,
    ) -> dict[str, Any] | None:
        """Get a specific quiz attempt."""

        pool = self._get_pool()

        row = await pool.fetchrow(
            """
            SELECT
                id,
                user_id,
                course,
                topic,
                score,
                total_items,
                percentage,
                completed_at
            FROM quiz_attempts
            WHERE id = $1
            """,
            attempt_id,
        )

        return dict(row) if row else None

    async def get_user_quiz_attempts(
        self,
        user_id: int,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Get a user's recent quiz attempts."""

        pool = self._get_pool()

        rows = await pool.fetch(
            """
            SELECT
                id,
                course,
                topic,
                score,
                total_items,
                percentage,
                completed_at
            FROM quiz_attempts
            WHERE user_id = $1
            ORDER BY completed_at DESC
            LIMIT $2
            """,
            user_id,
            limit,
        )

        return [dict(row) for row in rows]

    # ==========================================================
    # QUIZ ANSWERS
    # ==========================================================

    async def save_quiz_answer(
        self,
        attempt_id: int,
        question_id: str,
        selected_answer: str | None,
        correct_answer: str | None,
        is_correct: bool,
    ) -> int:
        """
        Save one answer from a quiz attempt.

        Returns the answer ID.
        """

        pool = self._get_pool()

        answer_id = await pool.fetchval(
            """
            INSERT INTO quiz_answers (
                attempt_id,
                question_id,
                selected_answer,
                correct_answer,
                is_correct
            )
            VALUES ($1, $2, $3, $4, $5)

            RETURNING id
            """,
            attempt_id,
            question_id,
            selected_answer,
            correct_answer,
            is_correct,
        )

        return int(answer_id)

    async def save_quiz_answers(
        self,
        attempt_id: int,
        answers: list[dict[str, Any]],
    ) -> None:
        """
        Save multiple quiz answers.

        Expected format:

        [
            {
                "question_id": "quiz-1",
                "selected_answer": "A",
                "correct_answer": "B",
                "is_correct": False,
            },
            ...
        ]
        """

        pool = self._get_pool()

        async with pool.acquire() as connection:
            async with connection.transaction():

                for answer in answers:
                    await connection.execute(
                        """
                        INSERT INTO quiz_answers (
                            attempt_id,
                            question_id,
                            selected_answer,
                            correct_answer,
                            is_correct
                        )
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        attempt_id,
                        answer["question_id"],
                        answer.get("selected_answer"),
                        answer.get("correct_answer"),
                        answer["is_correct"],
                    )

    async def get_quiz_answers(
        self,
        attempt_id: int,
    ) -> list[dict[str, Any]]:
        """Get all answers belonging to a quiz attempt."""

        pool = self._get_pool()

        rows = await pool.fetch(
            """
            SELECT
                id,
                question_id,
                selected_answer,
                correct_answer,
                is_correct
            FROM quiz_answers
            WHERE attempt_id = $1
            ORDER BY id ASC
            """,
            attempt_id,
        )

        return [dict(row) for row in rows]

    # ==========================================================
    # COMPLETE QUIZ SUBMISSION
    # ==========================================================

    async def save_complete_quiz(
        self,
        user_id: int,
        course: str,
        topic: str,
        score: int,
        total_items: int,
        answers: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Save a complete quiz attempt and all of its answers
        inside one PostgreSQL transaction.

        Returns:

        {
            "attempt_id": 1,
            "score": 8,
            "total_items": 10,
            "percentage": 80.0
        }
        """

        pool = self._get_pool()

        if total_items <= 0:
            raise ValueError("total_items must be greater than 0.")

        if score < 0 or score > total_items:
            raise ValueError(
                "score must be between 0 and total_items."
            )

        percentage = (score / total_items) * 100

        async with pool.acquire() as connection:
            async with connection.transaction():

                # ==================================================
                # ENSURE USER EXISTS
                # ==================================================

                await connection.execute(
                    """
                    INSERT INTO users (
                        user_id,
                        username,
                        display_name,
                        first_seen,
                        last_seen
                    )
                    VALUES (
                        $1,
                        $2,
                        $3,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )

                    ON CONFLICT (user_id)
                    DO UPDATE SET
                        last_seen = CURRENT_TIMESTAMP
                    """,
                    user_id,
                    str(user_id),
                    str(user_id),
                )

                # ==================================================
                # SAVE QUIZ ATTEMPT
                # ==================================================

                attempt_id = await connection.fetchval(
                    """
                    INSERT INTO quiz_attempts (
                        user_id,
                        course,
                        topic,
                        score,
                        total_items,
                        percentage
                    )
                    VALUES ($1, $2, $3, $4, $5, $6)

                    RETURNING id
                    """,
                    user_id,
                    course,
                    topic,
                    score,
                    total_items,
                    percentage,
                )

                # ==================================================
                # SAVE QUIZ ANSWERS
                # ==================================================

                for answer in answers:
                    await connection.execute(
                        """
                        INSERT INTO quiz_answers (
                            attempt_id,
                            question_id,
                            selected_answer,
                            correct_answer,
                            is_correct
                        )
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        attempt_id,
                        answer["question_id"],
                        answer.get("selected_answer"),
                        answer.get("correct_answer"),
                        answer["is_correct"],
                    )

        return {
            "attempt_id": int(attempt_id),
            "score": score,
            "total_items": total_items,
            "percentage": percentage,
        }

    # ==========================================================
    # ADMIN / REPORTING
    # ==========================================================