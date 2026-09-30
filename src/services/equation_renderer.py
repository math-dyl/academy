from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


class EquationRenderer:

    def __init__(
        self,
        base_path: Path,
    ):
        self.base_path = Path(base_path)
        self.output_path = (
            self.base_path
            / "data"
            / "generated"
            / "equations"
        )
        self.output_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==================================================
    # RENDER EQUATION
    # ==================================================

    def render(
        self,
        equation: str,
        filename: Optional[str] = None,
        dpi: int = 200,
    ) -> Optional[Path]:

        if not equation:
            return None

        equation = str(equation).strip()

        if not equation:
            return None

        if filename is None:
            equation_hash = hashlib.sha256(
                equation.encode("utf-8")
            ).hexdigest()[:16]

            filename = (
                f"equation_{equation_hash}.png"
            )

        output_file = (
            self.output_path / filename
        )

        try:

            formatted_equation = (
                self._format_equation(equation)
            )

            figure = plt.figure(
                figsize=(10, 2.0)
            )

            figure.patch.set_facecolor(
                "white"
            )

            figure.text(
                0.5,
                0.5,
                formatted_equation,
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=32,
            )

            figure.savefig(
                output_file,
                dpi=dpi,
                transparent=False,
                pad_inches=0.2,
                facecolor="white",
            )

            plt.close(figure)

            return output_file

        except Exception as error:

            plt.close("all")

            print(
                "[EquationRenderer] "
                f"Failed to render equation: {error}"
            )

            return None

    # ==================================================
    # RENDER MULTI-LINE EQUATION
    # ==================================================

    def render_block(
        self,
        content: str,
        filename: Optional[str] = None,
        dpi: int = 200,
    ) -> Optional[Path]:

        if not content:
            return None

        content = str(content).strip()

        if not content:
            return None

        if filename is None:

            content_hash = hashlib.sha256(
                content.encode("utf-8")
            ).hexdigest()[:16]

            filename = (
                f"equation_block_{content_hash}.png"
            )

        output_file = (
            self.output_path / filename
        )

        try:

            lines = (
                self._split_content_preserving_latex(
                    content
                )
            )

            if not lines:
                return None

            line_count = len(lines)

            figure_height = max(
                1.5,
                line_count * 0.8,
            )

            figure = plt.figure(
                figsize=(10, figure_height)
            )

            figure.patch.set_facecolor(
                "white"
            )

            for index, line in enumerate(lines):

                if not line.strip():
                    continue

                y_position = (
                    1
                    - (
                        index + 1
                    )
                    / (
                        line_count + 1
                    )
                )

                figure.text(
                    0.5,
                    y_position,
                    self._prepare_content_line(
                        line
                    ),
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=30,
                )

            figure.savefig(
                output_file,
                dpi=dpi,
                transparent=False,
                pad_inches=0.2,
                facecolor="white",
            )

            plt.close(figure)

            return output_file

        except Exception as error:

            plt.close("all")

            print(
                "[EquationRenderer] "
                f"Failed to render block: {error}"
            )

            return None

    # ==================================================
    # RENDER COMPLETE CONTENT
    # ==================================================

    def render_content(
        self,
        content: str,
        filename: Optional[str] = None,
        dpi: int = 200,
    ) -> Optional[Path]:

        if not content:
            return None

        content = str(content).strip()

        if not content:
            return None

        if filename is None:

            content_hash = hashlib.sha256(
                content.encode("utf-8")
            ).hexdigest()[:16]

            filename = (
                f"content_{content_hash}.png"
            )

        output_file = (
            self.output_path / filename
        )

        try:

            lines = (
                self._split_content_preserving_latex(
                    content
                )
            )

            if not lines:
                return None

            line_count = len(lines)

            # Increased vertical spacing
            figure_height = max(
                2.0,
                line_count * 1.1,
            )

            figure = plt.figure(
                figsize=(11, figure_height)
            )

            figure.patch.set_facecolor(
                "white"
            )

            for index, line in enumerate(lines):

                if not line.strip():
                    continue

                y_position = (
                    1
                    - (
                        index + 1
                    )
                    / (
                        line_count + 1
                    )
                )

                rendered_line = (
                    self._prepare_content_line(
                        line
                    )
                )

                figure.text(
                    0.05,
                    y_position,
                    rendered_line,
                    horizontalalignment="left",
                    verticalalignment="center",
                    fontsize=28,
                    wrap=True,
                )

            figure.savefig(
                output_file,
                dpi=dpi,
                transparent=False,
                pad_inches=0.3,
                facecolor="white",
            )

            plt.close(figure)

            return output_file

        except Exception as error:

            plt.close("all")

            print(
                "[EquationRenderer] "
                f"Failed to render content: {error}"
            )

            return None

    # ==================================================
    # SPLIT CONTENT WHILE PRESERVING LATEX
    # ==================================================

    @staticmethod
    def _split_content_preserving_latex(
        content: str,
    ) -> list[str]:

        content = str(content).replace(
            "\r\n",
            "\n",
        )

        content = content.replace(
            "\r",
            "\n",
        )

        # ------------------------------------------
        # NORMALIZE NEWLINES INSIDE INLINE MATH
        # ------------------------------------------
        content = re.sub(
            r"\$(.*?)\$",
            lambda match: (
                "$"
                + re.sub(
                    r"\s+",
                    " ",
                    match.group(1),
                ).strip()
                + "$"
            ),
            content,
            flags=re.DOTALL,
        )

        lines: list[str] = []

        current = ""

        math_mode = False
        math_delimiter = ""

        index = 0

        while index < len(content):

            char = content[index]

            # ------------------------------------------
            # $$ ... $$
            # ------------------------------------------

            if content.startswith(
                "$$",
                index,
            ):

                current += "$$"

                if (
                    math_mode
                    and math_delimiter == "$$"
                ):

                    math_mode = False
                    math_delimiter = ""

                elif not math_mode:

                    math_mode = True
                    math_delimiter = "$$"

                index += 2

                continue

            # ------------------------------------------
            # \[ ... \]
            # ------------------------------------------

            if content.startswith(
                r"\[",
                index,
            ):

                current += r"\["

                if not math_mode:

                    math_mode = True
                    math_delimiter = r"\["

                index += 2

                continue

            if content.startswith(
                r"\]",
                index,
            ):

                current += r"\]"

                if (
                    math_mode
                    and math_delimiter == r"\["
                ):

                    math_mode = False
                    math_delimiter = ""

                index += 2

                continue

            # ------------------------------------------
            # SINGLE $
            # ------------------------------------------

            if char == "$":

                current += char

                if (
                    index == 0
                    or content[index - 1] != "\\"
                ):

                    if not math_mode:

                        math_mode = True
                        math_delimiter = "$"

                    elif math_delimiter == "$":

                        math_mode = False
                        math_delimiter = ""

                index += 1

                continue

            # ------------------------------------------
            # NEWLINE
            # ------------------------------------------

            if char == "\n":

                if math_mode:

                    # Preserve newline inside LaTeX.
                    current += " "

                else:

                    if current.strip():

                        lines.append(
                            current.strip()
                        )

                    current = ""

                index += 1

                continue

            current += char

            index += 1

        if current.strip():

            lines.append(
                current.strip()
            )

        return lines

    # ==================================================
    # PREPARE CONTENT LINE
    # ==================================================

    @staticmethod
    def _prepare_content_line(
        line: str,
    ) -> str:

        line = str(line).strip()

        if not line:
            return ""

        # ----------------------------------------------
        # REMOVE MARKDOWN BOLD
        # ----------------------------------------------

        line = re.sub(
            r"\*\*(.*?)\*\*",
            r"\1",
            line,
        )

        # ----------------------------------------------
        # DISPLAY MATH
        # ----------------------------------------------

        line = re.sub(
            r"\$\$(.*?)\$\$",
            lambda match: (
                f"${match.group(1).strip()}$"
            ),
            line,
            flags=re.DOTALL,
        )

        # ----------------------------------------------
        # \[ ... \]
        # ----------------------------------------------

        line = re.sub(
            r"\\\[(.*?)\\\]",
            lambda match: (
                f"${match.group(1).strip()}$"
            ),
            line,
            flags=re.DOTALL,
        )

        # ----------------------------------------------
        # \( ... \)
        # ----------------------------------------------

        line = re.sub(
            r"\\\((.*?)\\\)",
            lambda match: (
                f"${match.group(1).strip()}$"
            ),
            line,
            flags=re.DOTALL,
        )

        # ----------------------------------------------
        # NORMALIZE WHITESPACE INSIDE LATEX
        # ----------------------------------------------

        def normalize_math(
            match,
        ):

            expression = (
                match.group(1)
                .replace("\n", " ")
            )

            expression = re.sub(
                r"\s+",
                " ",
                expression,
            )

            return (
                f"${expression.strip()}$"
            )

        line = re.sub(
            r"\$(.*?)\$",
            normalize_math,
            line,
            flags=re.DOTALL,
        )

        # ----------------------------------------------
        # BARE LATEX COMMANDS
        # ----------------------------------------------

        latex_command_pattern = re.compile(
            r"""
            (?<![\w$])
            (
                \\(?:frac|dfrac|tfrac|sqrt|sum|prod|int|lim)
                (?:\s*_[^{\s]+|\s*_\{[^}]*\})?
                (?:\s*\^[^{\s]+|\s*\^\{[^}]*\})?
                \s*
                \{[^{}]*\}
                (?:\s*\{[^{}]*\})?
            )
            (?![\w$])
            """,
            re.VERBOSE,
        )

        def wrap_latex_command(
            match,
        ):

            value = match.group(1).strip()

            return f"${value}$"

        # Only apply this to bare LaTeX commands
        # that are not already inside $...$.

        parts = re.split(
            r"(\$.*?\$)",
            line,
            flags=re.DOTALL,
        )

        for index in range(
            0,
            len(parts),
            2,
        ):

            parts[index] = (
                latex_command_pattern.sub(
                    wrap_latex_command,
                    parts[index],
                )
            )

        line = "".join(parts)

        # ----------------------------------------------
        # BARE POWERS
        # ----------------------------------------------

        power_pattern = re.compile(
            r"""
            (?<![\w$])
            (
                [A-Za-z]+
                \^
                [-+]?[A-Za-z0-9]+
            )
            (?![\w$])
            """,
            re.VERBOSE,
        )

        parts = re.split(
            r"(\$.*?\$)",
            line,
            flags=re.DOTALL,
        )

        for index in range(
            0,
            len(parts),
            2,
        ):

            parts[index] = power_pattern.sub(
                lambda match: (
                    f"${match.group(1)}$"
                ),
                parts[index],
            )

        line = "".join(parts)

        # ----------------------------------------------
        # BARE SUBSCRIPTS
        # ----------------------------------------------

        subscript_pattern = re.compile(
            r"""
            (?<![\w$])
            (
                [A-Za-z]+
                \_
                [-+]?[A-Za-z0-9]+
            )
            (?![\w$])
            """,
            re.VERBOSE,
        )

        parts = re.split(
            r"(\$.*?\$)",
            line,
            flags=re.DOTALL,
        )

        for index in range(
            0,
            len(parts),
            2,
        ):

            parts[index] = (
                subscript_pattern.sub(
                    lambda match: (
                        f"${match.group(1)}$"
                    ),
                    parts[index],
                )
            )

        line = "".join(parts)

        return line

    # ==================================================
    # FORMAT EQUATION
    # ==================================================

    @staticmethod
    def _format_equation(
        equation: str,
    ) -> str:

        equation = str(
            equation
        ).strip()

        # ----------------------------------------------
        # $$ ... $$
        # ----------------------------------------------

        if (
            equation.startswith("$$")
            and equation.endswith("$$")
        ):

            equation = equation[
                2:-2
            ].strip()

        # ----------------------------------------------
        # $ ... $
        # ----------------------------------------------

        elif (
            equation.startswith("$")
            and equation.endswith("$")
        ):

            equation = equation[
                1:-1
            ].strip()

        # ----------------------------------------------
        # \[ ... \]
        # ----------------------------------------------

        elif (
            equation.startswith(r"\[")
            and equation.endswith(r"\]")
        ):

            equation = equation[
                2:-2
            ].strip()

        # ----------------------------------------------
        # \( ... \)
        # ----------------------------------------------

        elif (
            equation.startswith(r"\(")
            and equation.endswith(r"\)")
        ):

            equation = equation[
                2:-2
            ].strip()

        # ----------------------------------------------
        # NORMALIZE WHITESPACE
        # ----------------------------------------------

        equation = equation.replace(
            "\n",
            " ",
        )

        equation = re.sub(
            r"\s+",
            " ",
            equation,
        )

        return f"${equation}$"

    # ==================================================
    # CHECK EQUATION
    # ==================================================

    @staticmethod
    def looks_like_equation(
        text: str,
    ) -> bool:

        if not text:
            return False

        text = str(text).strip()

        if not text:
            return False

        # ==============================================
        # EXPLICIT LATEX COMMANDS
        # ==============================================

        latex_indicators = (
            r"\frac",
            r"\dfrac",
            r"\tfrac",
            r"\sqrt",
            r"\sum",
            r"\prod",
            r"\int",
            r"\lim",
            r"\infty",
            r"\pi",
            r"\theta",
            r"\alpha",
            r"\beta",
            r"\gamma",
            r"\Delta",
            r"\partial",
            r"\nabla",
            r"\cdot",
            r"\times",
            r"\sin",
            r"\cos",
            r"\tan",
            r"\log",
            r"\ln",
            r"\exp",
            r"\left",
            r"\right",
            r"\leq",
            r"\geq",
            r"\neq",
            r"\approx",
        )

        if any(
            indicator in text
            for indicator in latex_indicators
        ):

            return True

        # ==============================================
        # MATH DELIMITERS
        # ==============================================

        if re.search(
            r"\$\$.*?\$\$",
            text,
            re.DOTALL,
        ):

            return True

        if re.search(
            r"\$[^$]+\$",
            text,
            re.DOTALL,
        ):

            return True

        if re.search(
            r"\\\[.*?\\\]",
            text,
            re.DOTALL,
        ):

            return True

        if re.search(
            r"\\\(.*?\\\)",
            text,
            re.DOTALL,
        ):

            return True

        # ==============================================
        # MATHEMATICAL SYMBOLS
        # ==============================================

        math_symbols = (
            "≤",
            "≥",
            "≠",
            "≈",
            "∫",
            "√",
            "∞",
            "∑",
            "∏",
            "∂",
            "∇",
            "±",
            "×",
            "÷",
        )

        if any(
            symbol in text
            for symbol in math_symbols
        ):

            return True

        # ==============================================
        # BARE EQUATION
        # ==============================================

        equation_pattern = re.compile(
            r"""
            (?<![\w$])
            [A-Za-z0-9]+
            (?:\s*[\^\_\\]\s*[-+]?[A-Za-z0-9]+)?
            (?:
                \s*[+\-*/]
                \s*
                [A-Za-z0-9]+
                (?:\s*[\^\_\\]\s*[-+]?[A-Za-z0-9]+)?
            )*
            \s*=\s*
            [A-Za-z0-9]+
            (?:\s*[\^\_\\]\s*[-+]?[A-Za-z0-9]+)?
            (?:
                \s*[+\-*/]
                \s*
                [A-Za-z0-9]+
                (?:\s*[\^\_\\]\s*[-+]?[A-Za-z0-9]+)?
            )*
            """,
            re.VERBOSE,
        )

        if equation_pattern.search(text):
            return True

        # ==============================================
        # BARE POWERS
        # ==============================================

        if re.search(
            r"(?<![\w$])[A-Za-z]+\^[-+]?[A-Za-z0-9]+(?![\w$])",
            text,
        ):

            return True

        # ==============================================
        # BARE SUBSCRIPTS
        # ==============================================

        if re.search(
            r"(?<![\w$])[A-Za-z]+_[-+]?[A-Za-z0-9]+(?![\w$])",
            text,
        ):

            return True

        return False