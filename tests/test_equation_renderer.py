import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib
from matplotlib.figure import Figure
from matplotlib.mathtext import MathTextParser
from PIL import Image, ImageChops

from src.services.equation_renderer import EquationRenderer


QUESTION = (
    r"Find the $8$th term of the geometric sequence $2, 6, 18, 54, \ldots$."
)
MULTILINE_QUESTION = (
    "Find the $\n8\n$th term of the geometric sequence "
    "$\n2, 6, 18, 54, \\ldots\n$."
)
CASES = [
    (QUESTION, [QUESTION]),
    (MULTILINE_QUESTION, [QUESTION]),
    ("$\n3\n$", ["$3$"]),
    (r"Solve $\frac{1}{2}x + 3 = 7$.", [r"Solve $\frac{1}{2}x + 3 = 7$."]),
    ("Evaluate:\n$$\n\\sum_{i=1}^{10} i\n$$", ["Evaluate:", r"$\sum_{i=1}^{10} i$"]),
    ("Find:\n\\[\n\\sqrt{x^2 + y^2}\n\\]", ["Find:", r"$\sqrt{x^2 + y^2}$"]),
    ("If $x_1 = 3$ and $x_2 = 5$, find $x_1 + x_2$.",
     ["If $x_1 = 3$ and $x_2 = 5$, find $x_1 + x_2$."]),
    (r"The value of $\pi$ is approximately $3.14159$.",
     [r"The value of $\pi$ is approximately $3.14159$."]),
    ("The sequence is $\n1, 2, 3, \\ldots\n$.", [r"The sequence is $1, 2, 3, \ldots$."]),
    ("Ordinary text with no mathematics should remain ordinary text.",
     ["Ordinary text with no mathematics should remain ordinary text."]),
]


class EquationRendererTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.renderer = EquationRenderer(Path(self.directory.name))

    def test_all_requested_cases_preserve_complete_math_spans(self):
        for content, expected in CASES:
            with self.subTest(content=content):
                self.assertEqual(
                    self.renderer._split_content_preserving_latex(content), expected,
                )
                for line in expected:
                    self.assertEqual(self.renderer._prepare_content_line(line), line)

    def test_all_delimiter_forms_and_standalone_equations(self):
        for content in (
            "$x$", "$ x $", "$\nx\n$", "$$x$$", "$$\nx\n$$",
            r"\(x\)", "\\(\nx\n\\)", "\\[\nx\n\\]",
        ):
            with self.subTest(content=content):
                self.assertEqual(self.renderer._normalize_latex_delimiters(content), "$x$")
                self.assertEqual(self.renderer._format_equation(content), "$x$")
                self.assertTrue(self.renderer.looks_like_equation(content))
                self.assertIsNotNone(self.renderer.render(content, dpi=80))
        self.assertEqual(self.renderer._format_equation("x^2 +\n3x"), "$x^2 + 3x$")

    def test_prose_whitespace_and_escaped_dollars(self):
        content = "First  line\r\nPay \\$5 or \\$10; $\r\nx^2   +   3x\r\n$.\r\nLast line"
        expected = "First  line\nPay \\$5 or \\$10; $x^2 + 3x$.\nLast line"
        self.assertEqual(self.renderer._normalize_latex_delimiters(content), expected)
        self.assertEqual(self.renderer._split_content_preserving_latex(content), expected.split("\n"))
        self.assertEqual(
            self.renderer._prepare_content_line(r"Pay \$5; use $x_1$ and x^2."),
            r"Pay \$5; use $x_1$ and $x^2$.",
        )
        self.assertFalse(self.renderer.looks_like_equation(r"Pay \$5 or \$10"))
        self.assertIsNotNone(self.renderer.render_content(content, dpi=80))

    def test_bare_math_and_bold_are_preserved(self):
        self.assertEqual(
            self.renderer._prepare_content_line(r"**Use** \frac{1}{2}, \dfrac{1}{2}, \sqrt{x}, x^2 and x_1."),
            r"Use $\frac{1}{2}$, $\dfrac{1}{2}$, $\sqrt{x}$, $x^2$ and $x_1$.",
        )
        self.assertEqual(self.renderer._format_equation(QUESTION), QUESTION)
        self.assertEqual(
            self.renderer._prepare_content_line(r"Use \ldots, \pi, \sum_{i=1}^{n} and \int_0^1."),
            r"Use $\ldots$, $\pi$, $\sum_{i=1}^{n}$ and $\int_0^1$.",
        )
        self.assertTrue(self.renderer.looks_like_equation(r"\ldots"))
        self.assertFalse(self.renderer.looks_like_equation(CASES[-1][0]))

    def test_math_commands_are_preserved_and_produce_math_glyphs(self):
        parser = MathTextParser("path")
        commands = (
            r"\frac{1}{2}", r"\dfrac{1}{2}", r"\sqrt{x}",
            r"\sum_{i=1}^{n}", r"\int_0^1", r"\pi", r"\theta",
            r"\alpha", r"\beta", r"\gamma", r"\Delta", r"\partial",
            r"\nabla", r"\cdot", r"\times", r"\sin", r"\cos", r"\tan",
            r"\log", r"\ln", r"\infty", r"\ldots",
        )
        for command in commands:
            with self.subTest(command=command):
                normalized = self.renderer._normalize_latex_delimiters("$\n" + command + "\n$")
                self.assertEqual(normalized, "$" + command + "$")
                glyphs = parser.parse(normalized).glyphs
                self.assertTrue(glyphs)
                self.assertNotIn(ord("$"), [glyph[2] for glyph in glyphs])
        self.assertEqual([g[2] for g in parser.parse(r"$\ldots$").glyphs], [0x2026])
        self.assertTrue(parser.parse(r"$\frac{1}{2}$").rects)
        self.assertIn(0x221A, [g[2] for g in parser.parse(r"$\sqrt{x}$").glyphs])
        for expression in ("$x^2$", "$x_1$"):
            glyphs = parser.parse(expression).glyphs
            self.assertNotEqual(glyphs[0][4], glyphs[1][4])

    def test_actual_pngs_use_mathtext_after_wrapping_even_if_disabled_globally(self):
        artists = []
        original_text = Figure.text

        def record_text(figure, *args, **kwargs):
            artist = original_text(figure, *args, **kwargs)
            artists.append(artist)
            return artist

        with matplotlib.rc_context({"text.parse_math": False, "text.usetex": True}):
            with patch.object(Figure, "text", record_text):
                for method in (self.renderer.render_content, self.renderer.render_block):
                    for number, (content, _) in enumerate(CASES, 1):
                        with self.subTest(method=method.__name__, case=number):
                            path = method(content, filename=f"{method.__name__}_{number}.png", dpi=80)
                            self.assertIsNotNone(path)
                            with Image.open(path) as image:
                                self.assertEqual(image.format, "PNG")
                                self.assertLess(image.convert("L").getextrema()[0], 255)
                self.assertIsNotNone(self.renderer.render(r"\frac{1}{2}x^2", dpi=80))

        for artist in artists:
            self.assertTrue(artist.get_parse_math())
            self.assertFalse(artist.get_usetex())
            self.assertFalse(artist.get_wrap())
            for line in artist.get_text().split("\n"):
                if "$" in line:
                    self.assertTrue(artist._preprocess_math(line)[1], line)

        for method in ("render_content", "render_block"):
            with Image.open(self.renderer.output_path / f"{method}_1.png") as first:
                with Image.open(self.renderer.output_path / f"{method}_2.png") as second:
                    self.assertEqual(first.size, second.size)
                    self.assertIsNone(ImageChops.difference(first.convert("RGB"), second.convert("RGB")).getbbox())

    def test_wrapping_preserves_math_spans_and_attached_prose(self):
        figure = Figure(figsize=(11, 2))
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        FigureCanvasAgg(figure)
        content = ("Some introductory words " * 8) + QUESTION
        lines = self.renderer._wrap_content_lines([content], figure, 28)
        self.assertGreater(len(lines), 1)
        self.assertEqual(" ".join(lines), content)
        self.assertTrue(any("$8$th" in line for line in lines))
        self.assertTrue(any(r"$2, 6, 18, 54, \ldots$." in line for line in lines))
        for line in lines:
            self.assertEqual(line.count("$") % 2, 0)

    def test_existing_hashed_output_is_regenerated(self):
        path = self.renderer.render_content(QUESTION, dpi=80)
        self.assertIsNotNone(path)
        path.write_bytes(b"stale image")
        self.assertEqual(self.renderer.render_content(QUESTION, dpi=80), path)
        self.assertEqual(path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()
