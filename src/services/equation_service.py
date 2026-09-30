from __future__ import annotations

import io
import re

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


class EquationService:

    # ==================================================
    # CONFIGURATION
    # ==================================================

    IMAGE_WIDTH = 12

    MAX_IMAGE_HEIGHT = 8.5

    TEXT_FONTSIZE = 21
    EQUATION_FONTSIZE = 26

    LINE_SPACING = 0.42
    EQUATION_SPACING = 1.10
    BLOCK_SPACING = 0.18

    TEXT_WRAP_LENGTH = 76

    TOP_MARGIN = 0.50
    SIDE_MARGIN = 0.65
    BOTTOM_MARGIN = 0.35

    # ==================================================
    # EQUATION PATTERNS
    # ==================================================

    # Display math:
    #
    # \[
    # x^2 + 4x + 1
    # \]
    #

    BLOCK_PATTERN = re.compile(
        r"\\\[(.*?)\\\]",
        re.DOTALL,
    )

    # Display math:
    #
    # $$
    # x^2 + 4x + 1
    # $$

    DOLLAR_PATTERN = re.compile(
        r"\$\$(.*?)\$\$",
        re.DOTALL,
    )

    # Inline math:
    #
    # $x^2 + 4x + 1$

    INLINE_DOLLAR_PATTERN = re.compile(
        r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)",
        re.DOTALL,
    )

    # Inline math:
    #
    # \(x^2 + 4x + 1\)

    INLINE_PAREN_PATTERN = re.compile(
        r"\\\((.*?)\\\)",
        re.DOTALL,
    )

    # ==================================================
    # BOLD PATTERN
    # ==================================================

    BOLD_PATTERN = re.compile(
        r"\*\*(.+?)\*\*",
        re.DOTALL,
    )

    # ==================================================
    # PARSE
    # ==================================================

    def parse(
        self,
        text: str,
    ):

        blocks = []

        position = 0

        # ------------------------------------------
        # Find display equations
        # ------------------------------------------

        matches = list(
            self.BLOCK_PATTERN.finditer(
                text
            )
        )

        matches += list(
            self.DOLLAR_PATTERN.finditer(
                text
            )
        )

        # ------------------------------------------
        # Sort display equations
        # ------------------------------------------

        matches.sort(
            key=lambda match: match.start()
        )

        # ------------------------------------------
        # Process display equations
        # ------------------------------------------

        for match in matches:

            before = text[
                position:match.start()
            ].strip()

            if before:

                blocks.append(
                    (
                        "text",
                        before,
                    )
                )

            equation = (
                match.group(1)
                .strip()
            )

            if equation:

                blocks.append(
                    (
                        "equation",
                        equation,
                    )
                )

            position = match.end()

        # ------------------------------------------
        # Remaining text
        # ------------------------------------------

        remaining = text[
            position:
        ].strip()

        if remaining:

            blocks.append(
                (
                    "text",
                    remaining,
                )
            )

        # ------------------------------------------
        # No display equations
        # ------------------------------------------

        if not blocks and text.strip():

            blocks.append(
                (
                    "text",
                    text.strip(),
                )
            )

        return blocks

    # ==================================================
    # HAS EQUATIONS
    # ==================================================

    def has_equations(
        self,
        text: str,
    ) -> bool:

        if self.BLOCK_PATTERN.search(text):

            return True

        if self.DOLLAR_PATTERN.search(text):

            return True

        if self.INLINE_DOLLAR_PATTERN.search(text):

            return True

        if self.INLINE_PAREN_PATTERN.search(text):

            return True

        return False

    # ==================================================
    # NORMALIZE INLINE MATH
    # ==================================================

    def normalize_inline_math(
        self,
        text: str,
    ) -> str:

        # ------------------------------------------
        # \( ... \) → $ ... $
        # ------------------------------------------

        text = (
            self.INLINE_PAREN_PATTERN.sub(
                lambda match: (
                    f"${match.group(1).strip()}$"
                ),
                text,
            )
        )

        return text

    # ==================================================
    # REMOVE MARKDOWN BOLD
    # ==================================================

    def normalize_bold(
        self,
        text: str,
    ) -> str:

        return (
            self.BOLD_PATTERN.sub(
                r"\1",
                text,
            )
        )

    # ==================================================
    # NORMALIZE TEXT
    # ==================================================

    def normalize_text(
        self,
        text: str,
    ) -> str:

        text = self.normalize_inline_math(
            text
        )

        text = self.normalize_bold(
            text
        )

        return text

    # ==================================================
    # TEXT WRAPPING
    # ==================================================

    def wrap_text(
        self,
        text: str,
    ):

        lines = []

        for paragraph in text.splitlines():

            paragraph = paragraph.strip()

            # --------------------------------------
            # Preserve empty lines
            # --------------------------------------

            if not paragraph:

                lines.append("")

                continue

            words = paragraph.split()

            current_line = ""

            for word in words:

                test_line = (
                    f"{current_line} {word}"
                    .strip()
                )

                # ----------------------------------
                # Wrap line
                # ----------------------------------

                if (
                    len(test_line)
                    > self.TEXT_WRAP_LENGTH
                ):

                    if current_line:

                        lines.append(
                            current_line
                        )

                    current_line = word

                else:

                    current_line = (
                        test_line
                    )

            # --------------------------------------
            # Remaining text
            # --------------------------------------

            if current_line:

                lines.append(
                    current_line
                )

        return lines

    # ==================================================
    # BLOCK HEIGHT
    # ==================================================

    def get_block_height(
        self,
        block_type: str,
        content: str,
    ) -> float:

        if block_type == "equation":

            return (
                self.EQUATION_SPACING
                + self.BLOCK_SPACING
            )

        lines = self.wrap_text(
            content
        )

        return (
            len(lines)
            * self.LINE_SPACING
            + self.BLOCK_SPACING
        )

    # ==================================================
    # RENDER SINGLE PAGE
    # ==================================================

    def render_page(
        self,
        blocks,
    ) -> io.BytesIO:

        # ------------------------------------------
        # Calculate page height
        # ------------------------------------------

        height = (
            self.TOP_MARGIN
            + self.BOTTOM_MARGIN
        )

        for block_type, content in blocks:

            if not content.strip():

                continue

            height += (
                self.get_block_height(
                    block_type,
                    content,
                )
            )

        height = max(
            height,
            2.0,
        )

        # ------------------------------------------
        # Create figure
        # ------------------------------------------

        figure = plt.figure(
            figsize=(
                self.IMAGE_WIDTH,
                height,
            ),
            facecolor="white",
        )

        # ------------------------------------------
        # Starting position
        # ------------------------------------------

        current_y = (
            height
            - self.TOP_MARGIN
        )

        # ------------------------------------------
        # Render blocks
        # ------------------------------------------

        for block_type, content in blocks:

            content = content.strip()

            if not content:

                continue

            # ======================================
            # TEXT
            # ======================================

            if block_type == "text":

                lines = self.wrap_text(
                    content
                )

                for line in lines:

                    # ----------------------------------
                    # Empty line
                    # ----------------------------------

                    if not line:

                        current_y -= (
                            self.LINE_SPACING
                        )

                        continue

                    # ----------------------------------
                    # Normalize Markdown + LaTeX
                    # ----------------------------------

                    line = self.normalize_text(
                        line
                    )

                    # ----------------------------------
                    # Draw text
                    # ----------------------------------

                    figure.text(
                        self.SIDE_MARGIN
                        / self.IMAGE_WIDTH,

                        current_y
                        / height,

                        line,

                        ha="left",
                        va="top",

                        fontsize=(
                            self.TEXT_FONTSIZE
                        ),

                        color="black",
                    )

                    current_y -= (
                        self.LINE_SPACING
                    )

                current_y -= (
                    self.BLOCK_SPACING
                )

            # ======================================
            # DISPLAY EQUATION
            # ======================================

            elif block_type == "equation":

                # ----------------------------------
                # ALWAYS CENTER EQUATION
                # ----------------------------------

                figure.text(
                    0.5,

                    current_y
                    / height,

                    f"${content}$",

                    ha="center",
                    va="top",

                    fontsize=(
                        self.EQUATION_FONTSIZE
                    ),

                    color="black",
                )

                current_y -= (
                    self.EQUATION_SPACING
                )

                current_y -= (
                    self.BLOCK_SPACING
                )

        # ------------------------------------------
        # Save image
        # ------------------------------------------

        buffer = io.BytesIO()

        figure.savefig(
            buffer,
            format="png",
            facecolor="white",
            edgecolor="none",
            pad_inches=0.30,
            dpi=180,
        )

        plt.close(
            figure
        )

        buffer.seek(0)

        return buffer

    # ==================================================
    # SPLIT BLOCKS INTO PAGES
    # ==================================================

    def split_pages(
        self,
        blocks,
    ):

        pages = []

        current_page = []

        current_height = (
            self.TOP_MARGIN
            + self.BOTTOM_MARGIN
        )

        for block_type, content in blocks:

            if not content.strip():

                continue

            block_height = (
                self.get_block_height(
                    block_type,
                    content,
                )
            )

            # ------------------------------------------
            # Start new page if necessary
            # ------------------------------------------

            if (
                current_page
                and (
                    current_height
                    + block_height
                    > self.MAX_IMAGE_HEIGHT
                )
            ):

                pages.append(
                    current_page
                )

                current_page = []

                current_height = (
                    self.TOP_MARGIN
                    + self.BOTTOM_MARGIN
                )

            # ------------------------------------------
            # Add block
            # ------------------------------------------

            current_page.append(
                (
                    block_type,
                    content,
                )
            )

            current_height += (
                block_height
            )

        # ------------------------------------------
        # Add remaining page
        # ------------------------------------------

        if current_page:

            pages.append(
                current_page
            )

        return pages

    # ==================================================
    # RENDER SINGLE FORMULA
    # ==================================================

    def render_formula_cheatsheet(
        self,
        title: str,
        formulas: list[dict],
    ) -> io.BytesIO:
        """
        Render a complete formula cheatsheet using the same
        fixed-width white canvas style as the /ask renderer.
        """

        # ==================================================
        # CONFIGURATION
        # ==================================================

        TITLE_FONTSIZE = 28
        NAME_FONTSIZE = 18
        EQUATION_FONTSIZE = self.EQUATION_FONTSIZE

        # Use the SAME width as /ask
        FIGURE_WIDTH = self.IMAGE_WIDTH

        TOP_PADDING = 0.45
        BOTTOM_PADDING = 0.35

        TITLE_HEIGHT = 0.55
        TITLE_GAP = 0.30

        NAME_HEIGHT = 0.32
        NAME_GAP = 0.12

        EQUATION_HEIGHT = 0.65
        EQUATION_GAP = 0.38

        FORMULA_SPACING = 0.35

        DPI = 180

        # ==================================================
        # Prepare formulas
        # ==================================================

        valid_formulas = []

        for item in formulas:
            name = item.get("name", "Formula")
            formula = item.get("formula", "").strip()

            if not formula:
                continue

            valid_formulas.append(
                {
                    "name": name,
                    "formula": formula,
                }
            )

        if not valid_formulas:
            raise ValueError(
                "No valid formulas to render."
            )

        # ==================================================
        # Calculate height
        # ==================================================

        formula_block_height = (
            NAME_HEIGHT
            + NAME_GAP
            + EQUATION_HEIGHT
            + EQUATION_GAP
        )

        figure_height = (
            TOP_PADDING
            + TITLE_HEIGHT
            + TITLE_GAP
            + (
                len(valid_formulas)
                * formula_block_height
            )
            + (
                max(
                    0,
                    len(valid_formulas) - 1,
                )
                * FORMULA_SPACING
            )
            + BOTTOM_PADDING
        )

        figure_height = max(
            figure_height,
            3.0,
        )

        # ==================================================
        # Create fixed-width figure
        # ==================================================

        figure = plt.figure(
            figsize=(
                FIGURE_WIDTH,
                figure_height,
            ),
            facecolor="white",
        )

        # ==================================================
        # Title
        # ==================================================

        y = (
            1.0
            - (
                TOP_PADDING
                / figure_height
            )
        )

        figure.text(
            0.5,
            y,
            title,
            ha="center",
            va="top",
            fontsize=TITLE_FONTSIZE,
            fontweight="bold",
            color="black",
        )

        y -= (
            TITLE_HEIGHT
            + TITLE_GAP
        ) / figure_height

        # ==================================================
        # Render formulas
        # ==================================================

        for index, item in enumerate(valid_formulas):

            name = item["name"]
            formula = item["formula"]

            # ----------------------------------------------
            # Formula name
            # ----------------------------------------------

            figure.text(
                0.5,
                y,
                name,
                ha="center",
                va="top",
                fontsize=NAME_FONTSIZE,
                fontweight="bold",
                color="black",
            )

            y -= (
                NAME_HEIGHT
                + NAME_GAP
            ) / figure_height

            # ----------------------------------------------
            # Equation
            # ----------------------------------------------

            figure.text(
                0.5,
                y,
                f"${formula}$",
                ha="center",
                va="top",
                fontsize=EQUATION_FONTSIZE,
                color="black",
            )

            y -= (
                EQUATION_HEIGHT
                + EQUATION_GAP
            ) / figure_height

            # ----------------------------------------------
            # Space between formulas
            # ----------------------------------------------

            if index < len(valid_formulas) - 1:
                y -= (
                    FORMULA_SPACING
                    / figure_height
                )

        # ==================================================
        # Save
        # ==================================================

        buffer = io.BytesIO()

        figure.savefig(
            buffer,
            format="png",
            facecolor="white",
            edgecolor="none",
            pad_inches=0.20,
            dpi=DPI,
        )

        plt.close(figure)

        buffer.seek(0)

        return buffer

    def render_formula(
        self,
        formula: str,
    ) -> io.BytesIO:

        formula = formula.strip()

        # ------------------------------------------
        # Dynamic width based on formula length
        # ------------------------------------------

        formula_length = len(formula)

        if formula_length <= 20:
            width = 5.0
        elif formula_length <= 40:
            width = 7.0
        elif formula_length <= 70:
            width = 9.0
        else:
            width = 11.0

        # ------------------------------------------
        # Create figure
        # ------------------------------------------

        figure = plt.figure(
            figsize=(
                width,
                1.65,
            ),
            facecolor="white",
        )

        # ------------------------------------------
        # Render LaTeX equation
        #
        # Keep the equation centered dynamically.
        # Matplotlib handles:
        # - fractions
        # - superscripts
        # - subscripts
        # - limits
        # - mathematical symbols
        # ------------------------------------------

        figure.text(
            0.5,
            0.50,
            f"${formula}$",
            ha="center",
            va="center",
            fontsize=self.EQUATION_FONTSIZE,
            color="black",
        )

        # ------------------------------------------
        # Save image
        # ------------------------------------------

        buffer = io.BytesIO()

        figure.savefig(
            buffer,
            format="png",
            facecolor="white",
            edgecolor="none",
            bbox_inches="tight",
            pad_inches=0.25,
            dpi=180,
        )

        plt.close(
            figure
        )

        buffer.seek(0)

        return buffer


    # ==================================================
    # RENDER RESPONSE
    # ==================================================

    def render_response(
        self,
        blocks,
    ) -> list[io.BytesIO] | None:

        # ------------------------------------------
        # Check whether response contains math
        # ------------------------------------------

        has_math = False

        for block_type, content in blocks:

            if block_type == "equation":

                has_math = True

                break

            if (
                block_type == "text"
                and self.has_equations(
                    content
                )
            ):

                has_math = True

                break

        # ------------------------------------------
        # No equation
        #
        # Do not generate images.
        # ------------------------------------------

        if not has_math:

            return None

        # ------------------------------------------
        # Split response into pages
        # ------------------------------------------

        pages = self.split_pages(
            blocks
        )

        # ------------------------------------------
        # Render every page
        # ------------------------------------------

        images = []

        for page_blocks in pages:

            image = self.render_page(
                page_blocks
            )

            images.append(
                image
            )

        return images