from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class PDFService:

    # ==================================================
    # CREATE QUIZ PDF
    # ==================================================

    def create_quiz_pdf(
        self,
        course: str,
        topic: str,
        questions: list[dict],
        answers: list[dict],
        score: int,
    ) -> BytesIO:

        total = len(
            questions
        )

        percentage = (
            (score / total) * 100
            if total
            else 0
        )

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.6 * inch,
            leftMargin=0.6 * inch,
            topMargin=0.6 * inch,
            bottomMargin=0.6 * inch,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "QuizTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            spaceAfter=8,
        )

        subtitle_style = ParagraphStyle(
            "QuizSubtitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=20,
        )

        question_style = ParagraphStyle(
            "Question",
            parent=styles["Heading3"],
            fontSize=11,
            leading=15,
            spaceAfter=7,
        )

        normal_style = ParagraphStyle(
            "ReviewNormal",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=14,
            spaceAfter=5,
        )

        correct_style = ParagraphStyle(
            "Correct",
            parent=normal_style,
            textColor=colors.green,
        )

        incorrect_style = ParagraphStyle(
            "Incorrect",
            parent=normal_style,
            textColor=colors.red,
        )

        story = []

        # ==================================================
        # HEADER
        # ==================================================

        story.append(
            Paragraph(
                "Mathdyl Academy",
                title_style,
            )
        )

        story.append(
            Paragraph(
                "Quiz Review",
                subtitle_style,
            )
        )

        # ==================================================
        # INFORMATION
        # ==================================================

        info_data = [
            [
                Paragraph(
                    "<b>Course</b>",
                    normal_style,
                ),
                Paragraph(
                    escape(str(course)),
                    normal_style,
                ),
            ],
            [
                Paragraph(
                    "<b>Topic</b>",
                    normal_style,
                ),
                Paragraph(
                    escape(str(topic)),
                    normal_style,
                ),
            ],
            [
                Paragraph(
                    "<b>Score</b>",
                    normal_style,
                ),
                Paragraph(
                    f"{score}/{total}",
                    normal_style,
                ),
            ],
            [
                Paragraph(
                    "<b>Percentage</b>",
                    normal_style,
                ),
                Paragraph(
                    f"{percentage:.1f}%",
                    normal_style,
                ),
            ],
        ]

        info_table = Table(
            info_data,
            colWidths=[
                1.4 * inch,
                5.3 * inch,
            ],
        )

        info_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(
            info_table
        )

        story.append(
            Spacer(1, 20)
        )

        # ==================================================
        # QUESTION REVIEW
        # ==================================================

        for index, question in enumerate(
            questions
        ):

            result = (
                answers[index]
                if index < len(answers)
                else {}
            )

            question_text = question.get(
                "question",
                question.get(
                    "problem",
                    "",
                ),
            )

            user_answer = result.get(
                "user_answer",
                "No answer",
            )

            correct_answer = result.get(
                "correct_answer",
                question.get(
                    "answer",
                    question.get(
                        "correct_answer",
                        "Unknown",
                    ),
                ),
            )

            is_correct = result.get(
                "correct",
                False,
            )

            explanation = question.get(
                "explanation",
                question.get(
                    "solution",
                    question.get(
                        "answer_explanation",
                        "",
                    ),
                ),
            )

            question_block = []

            question_block.append(
                Paragraph(
                    (
                        f"<b>{index + 1}. "
                        f"{escape(str(question_text))}</b>"
                    ),
                    question_style,
                )
            )

            # ----------------------------------------------
            # OPTIONS
            # ----------------------------------------------

            options = question.get(
                "options",
                [],
            )

            if options:

                letters = (
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                )

                option_text = "<br/>".join(
                    (
                        f"<b>{letters[i]}.</b> "
                        f"{escape(str(option))}"
                    )
                    for i, option in enumerate(
                        options
                    )
                )

                question_block.append(
                    Paragraph(
                        option_text,
                        normal_style,
                    )
                )

                question_block.append(
                    Spacer(1, 5)
                )

            # ----------------------------------------------
            # USER ANSWER
            # ----------------------------------------------

            question_block.append(
                Paragraph(
                    (
                        "<b>Your Answer:</b> "
                        f"{escape(str(user_answer))}"
                    ),
                    normal_style,
                )
            )

            # ----------------------------------------------
            # CORRECT ANSWER
            # ----------------------------------------------

            question_block.append(
                Paragraph(
                    (
                        "<b>Correct Answer:</b> "
                        f"{escape(str(correct_answer))}"
                    ),
                    normal_style,
                )
            )

            # ----------------------------------------------
            # STATUS
            # ----------------------------------------------

            if is_correct:

                question_block.append(
                    Paragraph(
                        "<b>Status:</b> Correct",
                        correct_style,
                    )
                )

            else:

                question_block.append(
                    Paragraph(
                        "<b>Status:</b> Incorrect",
                        incorrect_style,
                    )
                )

            # ----------------------------------------------
            # EXPLANATION
            # ----------------------------------------------

            if explanation:

                question_block.append(
                    Paragraph(
                        (
                            "<b>Explanation:</b> "
                            f"{escape(str(explanation))}"
                        ),
                        normal_style,
                    )
                )

            else:

                question_block.append(
                    Paragraph(
                        (
                            "<b>Explanation:</b> "
                            "No explanation provided."
                        ),
                        normal_style,
                    )
                )

            question_block.append(
                Spacer(1, 14)
            )

            story.append(
                KeepTogether(
                    question_block
                )
            )

        # ==================================================
        # FOOTER
        # ==================================================

        story.append(
            Spacer(1, 10)
        )

        story.append(
            Paragraph(
                "Mathdyl Academy • "
                "Keep learning. Keep building.",
                subtitle_style,
            )
        )

        document.build(
            story
        )

        buffer.seek(0)

        return buffer