from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import cbook
from matplotlib.font_manager import FontProperties


class EquationRenderer:

    # Match escaped backslashes/dollars first so they cannot open math.
    # Inside a math span, escaped characters belong to the expression.
    _LATEX_TOKEN_PATTERN = re.compile(
        r"(?P<escaped>\\[\\$])"
        r"|(?P<math>"
        r"\$\$(?:\\.|[^\\])*?\$\$"
        r"|\$(?:\\.|[^\\$])*?\$"
        r"|\\\((?:\\.|[^\\])*?\\\)"
        r"|\\\[(?:\\.|[^\\])*?\\\]"
        r")",
        re.DOTALL,
    )

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
                parse_math=True,
                usetex=False,
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
                    parse_math=True,
                    usetex=False,
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

            figure = plt.figure(figsize=(11, 2.0))
            lines = self._wrap_content_lines(
                [self._prepare_content_line(line) for line in lines],
                figure,
                fontsize=28,
            )
            line_count = len(lines)
            figure_height = max(2.0, line_count * 1.1)
            figure.set_size_inches(11, figure_height)

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

                rendered_line = line

                figure.text(
                    0.05,
                    y_position,
                    rendered_line,
                    horizontalalignment="left",
                    verticalalignment="center",
                    fontsize=28,
                    wrap=False,
                    parse_math=True,
                    usetex=False,
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
    # NORMALIZE AND SPLIT LATEX
    # ==================================================

    @staticmethod
    def _normalize_latex_delimiters(content: str) -> str:
        """Convert complete math spans to mathtext without changing prose."""
        content = str(content).replace("\r\n", "\n").replace("\r", "\n")

        def normalize(match: re.Match) -> str:
            if match.lastgroup != "math":
                return match.group(0)

            value = match.group(0)
            delimiter_length = (
                1 if value.startswith("$") and not value.startswith("$$") else 2
            )
            expression = re.sub(
                r"\s+", " ", value[delimiter_length:-delimiter_length],
            ).strip()
            return f"${expression}$" if expression else ""

        return EquationRenderer._LATEX_TOKEN_PATTERN.sub(normalize, content)

    @staticmethod
    def _split_math_parts(content: str) -> list[str]:
        """Return alternating prose/math spans, ignoring escaped dollars."""
        parts = []
        position = 0
        for match in EquationRenderer._LATEX_TOKEN_PATTERN.finditer(content):
            if match.lastgroup == "math":
                parts.extend((content[position:match.start()], match.group(0)))
                position = match.end()
        parts.append(content[position:])
        return parts

    @staticmethod
    def _split_content_preserving_latex(content: str) -> list[str]:
        # Complete math spans have no newlines after normalization. Newlines
        # in prose retain their existing meaning as visual line breaks.
        content = EquationRenderer._normalize_latex_delimiters(content)
        return [line.strip() for line in content.split("\n") if line.strip()]

    @staticmethod
    def _wrap_content_lines(lines: list[str], figure, fontsize: int) -> list[str]:
        """Wrap prose by measured width, keeping each math span indivisible."""
        renderer = figure.canvas.get_renderer()
        font = FontProperties(size=fontsize)
        available_width = figure.bbox.width * 0.9
        wrapped = []

        for line in lines:
            # Keep math attached to adjacent prose (e.g. "$8$th" or "$x$.").
            tokens = []
            for index, part in enumerate(EquationRenderer._split_math_parts(line)):
                if index % 2:
                    pieces = [part]
                else:
                    pieces = re.split(r"(\s+)", part)
                for piece in pieces:
                    if not piece:
                        continue
                    if tokens and not tokens[-1].isspace() and not piece.isspace():
                        tokens[-1] += piece
                    else:
                        tokens.append(piece)

            current = ""
            for token in tokens:
                candidate = current + token
                if not token.isspace():
                    width, _, _ = renderer.get_text_width_height_descent(
                        candidate, font, ismath=cbook.is_math_text(candidate),
                    )
                    if current.strip() and width > available_width:
                        wrapped.append(current.rstrip())
                        current = token
                        continue
                current = candidate
            if current.strip():
                wrapped.append(current.rstrip())

        return wrapped

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

        line = EquationRenderer._normalize_latex_delimiters(line)

        # ----------------------------------------------
        # BARE LATEX COMMANDS
        # ----------------------------------------------

        latex_command_pattern = re.compile(
            r"""
            (?<![\w$])
            (
                \\(?:frac|dfrac|tfrac|sqrt)
                \s*\{[^{}]*\}(?:\s*\{[^{}]*\})?
                |
                \\(?:sum|prod|int|lim)
                (?:\s*[_^](?:\{[^}]*\}|[-+]?[A-Za-z0-9])){0,2}
                (?:\s*\{[^{}]*\})?
                |
                \\(?:pi|theta|alpha|beta|gamma|Delta|partial|nabla|
                     cdot|times|sin|cos|tan|log|ln|exp|infty|ldots|
                     leq|geq|neq|approx)\b
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

        parts = EquationRenderer._split_math_parts(line)

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

        parts = EquationRenderer._split_math_parts(line)

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

        parts = EquationRenderer._split_math_parts(line)

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

        equation = EquationRenderer._normalize_latex_delimiters(equation).strip()
        parts = EquationRenderer._split_math_parts(equation)
        if len(parts) > 1:
            # Already delimited equations (or mixed text) must not be wrapped
            # again: nested dollar delimiters disable mathtext parsing.
            return equation

        equation = re.sub(r"\s+", " ", equation)
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
            r"\ldots",
        )

        if any(
            indicator in text
            for indicator in latex_indicators
        ):

            return True

        # Complete math spans are recognized by the same escape-aware parser
        # used for normalization and wrapping.
        if len(EquationRenderer._split_math_parts(text)) > 1:
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
