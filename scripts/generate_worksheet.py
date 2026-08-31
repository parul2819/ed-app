"""Generate print-ready A4 PDF practice worksheets for Class 3 Maths.

All arithmetic here is generated programmatically with Python's random
module -- never pulled from the LLM-generated question bank in
content/questions/ -- so the answer key is guaranteed correct by
construction: it is computed from the exact same (a, op, b) values used to
print each question, not re-derived or re-typed.

Usage:
    poetry run python scripts/generate_worksheet.py --topic addition --set "Set A" --seed 1 --out worksheet.pdf
    poetry run python scripts/generate_worksheet.py --topic multiplication --set "Set B" --seed 2 --out mul_set_b.pdf
"""

import argparse
import math
import random
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = A4
MARGIN = 15 * mm

INK = colors.HexColor("#2B2B2B")
LINE_GRAY = colors.HexColor("#B8B8B8")

SKY_BLUE = colors.HexColor("#BDEBFF")
HEADING_PURPLE = colors.HexColor("#7457C9")

GRASS_GREEN = colors.HexColor("#8BC34A")
GRASS_GREEN_DARK = colors.HexColor("#6FA83A")

CREAM = colors.HexColor("#FFF8E7")
CREAM_BORDER = colors.HexColor("#F0DCA0")
STAR_OUTLINE = colors.HexColor("#F5A623")

OWL_PURPLE = colors.HexColor("#8C6FE0")
OWL_PURPLE_DARK = colors.HexColor("#7457C9")
OWL_PINK = colors.HexColor("#FFD1E3")
OWL_YELLOW = colors.HexColor("#FFC94A")
OWL_STRING_GRAY = colors.HexColor("#8A8A8A")

BALLOON_COLORS = [
    colors.HexColor("#FF8FA3"),
    colors.HexColor("#FFD54F"),
    colors.HexColor("#81D4FA"),
]

# (light fill, darker accent) pairs the sum boxes and word-problem cards
# cycle through, five to a set so no two adjacent boxes ever match.
PASTELS = [
    (colors.HexColor("#FFE1E9"), colors.HexColor("#FF7FA3")),
    (colors.HexColor("#E1F3FF"), colors.HexColor("#4FC3F7")),
    (colors.HexColor("#FFF6D6"), colors.HexColor("#FFC94A")),
    (colors.HexColor("#E3F7E3"), colors.HexColor("#7CC576")),
    (colors.HexColor("#F1E6FA"), colors.HexColor("#B27FE0")),
]

BANNER_COLOR = colors.HexColor("#4FC3F7")
FOOTER_GREEN = colors.HexColor("#8BC34A")

TOPIC_TITLES = {
    "addition": "Addition Practice",
    "subtraction": "Subtraction Practice",
    "multiplication": "Multiplication Practice",
    "division": "Division Practice",
}
TOPIC_SYMBOLS = {"addition": "+", "subtraction": "-", "multiplication": "x", "division": "÷"}

NAMES = ["Priya", "Rohan", "Aisha", "Kabir", "Meera", "Arjun", "Diya", "Vihaan", "Sara", "Ishaan"]
ADD_SUB_OBJECTS = ["marbles", "stickers", "pencils", "stamps", "candies", "balloons"]
MUL_CONTAINERS = ["boxes", "baskets", "bags", "trays", "shelves"]
MUL_ITEMS = ["pencils", "apples", "candies", "toys", "stickers", "flowers"]
DIV_ITEMS = ["marbles", "stickers", "pencils", "candies", "flowers", "toys"]

SUMS_PER_WORKSHEET = 20
WORD_PROBLEMS_PER_WORKSHEET = 3
GRID_COLUMNS = 5


def _apply_op(a: int, op: str, b: int) -> int:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "÷":
        return a // b
    return a * b  # "x"


@dataclass(frozen=True)
class ColumnSum:
    a: int
    b: int
    op: str
    answer: int


@dataclass(frozen=True)
class WordProblem:
    text: str
    a: int
    b: int
    op: str
    answer: int


@dataclass(frozen=True)
class WorksheetData:
    topic: str
    sums: list[ColumnSum]
    word_problems: list[WordProblem]


def _random_operand(rng: random.Random, digits: int) -> int:
    lo, hi = 10 ** (digits - 1), 10**digits - 1
    return rng.randint(lo, hi)


def generate_column_sums(
    topic: str, rng: random.Random, count: int = SUMS_PER_WORKSHEET
) -> list[ColumnSum]:
    """Generate `count` column-format sums for `topic`.

    Addition/subtraction operands are 2 or 3 digits each (chosen
    independently per operand, per sum, for variety); subtraction operands
    are ordered so the result is always non-negative. Multiplication
    operands are single digits 1-9.
    """
    sums = []
    for _ in range(count):
        if topic == "multiplication":
            a, b = rng.randint(1, 9), rng.randint(1, 9)
            sums.append(ColumnSum(a, b, "x", a * b))
        elif topic == "addition":
            a = _random_operand(rng, rng.choice([2, 3]))
            b = _random_operand(rng, rng.choice([2, 3]))
            sums.append(ColumnSum(a, b, "+", a + b))
        elif topic == "subtraction":
            a = _random_operand(rng, rng.choice([2, 3]))
            b = _random_operand(rng, rng.choice([2, 3]))
            hi, lo = max(a, b), min(a, b)
            sums.append(ColumnSum(hi, lo, "-", hi - lo))
        elif topic == "division":
            divisor, quotient = rng.randint(1, 9), rng.randint(1, 9)
            sums.append(ColumnSum(divisor * quotient, divisor, "÷", quotient))
        else:
            raise ValueError(f"Unknown topic {topic!r}")
    return sums


def generate_word_problems(
    topic: str, rng: random.Random, count: int = WORD_PROBLEMS_PER_WORKSHEET
) -> list[WordProblem]:
    """Generate `count` word problems for `topic`, using the same digit and
    operand rules as generate_column_sums (see there for details)."""
    problems = []
    for _ in range(count):
        if topic == "addition":
            name = rng.choice(NAMES)
            obj = rng.choice(ADD_SUB_OBJECTS)
            a = _random_operand(rng, rng.choice([2, 3]))
            b = _random_operand(rng, rng.choice([2, 3]))
            text = (
                f"{name} has {a} {obj}. They get {b} more {obj}. "
                f"How many {obj} do they have now?"
            )
            problems.append(WordProblem(text, a, b, "+", a + b))
        elif topic == "subtraction":
            name = rng.choice(NAMES)
            obj = rng.choice(ADD_SUB_OBJECTS)
            a = _random_operand(rng, rng.choice([2, 3]))
            b = _random_operand(rng, rng.choice([2, 3]))
            hi, lo = max(a, b), min(a, b)
            text = (
                f"{name} has {hi} {obj}. They give away {lo} {obj}. "
                f"How many {obj} do they have left?"
            )
            problems.append(WordProblem(text, hi, lo, "-", hi - lo))
        elif topic == "multiplication":
            container = rng.choice(MUL_CONTAINERS)
            item = rng.choice(MUL_ITEMS)
            a, b = rng.randint(1, 9), rng.randint(1, 9)
            text = (
                f"There are {a} {container} with {b} {item} in each. "
                f"How many {item} are there in total?"
            )
            problems.append(WordProblem(text, a, b, "x", a * b))
        elif topic == "division":
            name = rng.choice(NAMES)
            item = rng.choice(DIV_ITEMS)
            divisor, quotient = rng.randint(1, 9), rng.randint(1, 9)
            dividend = divisor * quotient
            text = (
                f"{name} has {dividend} {item} to share equally among {divisor} friends. "
                f"How many {item} will each friend get?"
            )
            problems.append(WordProblem(text, dividend, divisor, "÷", quotient))
        else:
            raise ValueError(f"Unknown topic {topic!r}")
    return problems


def generate_worksheet_data(topic: str, seed: int) -> WorksheetData:
    """Generate one worksheet's worth of sums + word problems.

    Deterministic in `seed`: the same (topic, seed) pair always produces the
    same questions, so --seed gives reproducible variation across runs.
    """
    if topic not in TOPIC_TITLES:
        raise ValueError(f"Unknown topic {topic!r}; expected one of {sorted(TOPIC_TITLES)}")
    rng = random.Random(seed)
    sums = generate_column_sums(topic, rng)
    word_problems = generate_word_problems(topic, rng)
    return WorksheetData(topic=topic, sums=sums, word_problems=word_problems)


# --- PDF rendering -----------------------------------------------------
# Pure layout/decoration code below; none of it touches the arithmetic
# above, which is what the answer key's correctness depends on.

HEADER_H = 40 * mm
GRASS_H = 6 * mm


def _star_points(cx: float, cy: float, r_outer: float, r_inner: float) -> list[tuple[float, float]]:
    points = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = r_outer if i % 2 == 0 else r_inner
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return points


def _draw_star(c: canvas.Canvas, cx: float, cy: float, r_outer: float, stroke_color) -> None:
    """Draw a 5-pointed star outline (no fill) a child can colour in."""
    pts = _star_points(cx, cy, r_outer, r_outer * 0.42)
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    c.setStrokeColor(stroke_color)
    c.setLineWidth(1.1)
    c.drawPath(p, fill=0, stroke=1)


def _draw_cloud(c: canvas.Canvas, cx: float, cy: float, w: float = 16 * mm) -> None:
    """A few overlapping white ellipses make a simple puffy cloud."""
    h = w * 0.5
    c.setFillColor(colors.white)
    c.ellipse(cx - w * 0.5, cy - h * 0.4, cx + w * 0.5, cy + h * 0.4, fill=1, stroke=0)
    c.ellipse(cx - w * 0.62, cy - h * 0.35, cx - w * 0.12, cy + h * 0.25, fill=1, stroke=0)
    c.ellipse(cx + w * 0.12, cy - h * 0.35, cx + w * 0.62, cy + h * 0.25, fill=1, stroke=0)
    c.ellipse(cx - w * 0.22, cy - h * 0.1, cx + w * 0.22, cy + h * 0.55, fill=1, stroke=0)


def _draw_owl(c: canvas.Canvas, cx: float, cy: float, scale: float = 1.0) -> None:
    """A friendly owl mascot built from ellipses and simple paths."""
    body_w, body_h = 22 * mm * scale, 26 * mm * scale

    # Feet (drawn first, so the body overlaps their tops).
    foot_w, foot_h = 5 * mm * scale, 3 * mm * scale
    c.setFillColor(OWL_YELLOW)
    for dx in (-body_w * 0.32, body_w * 0.32):
        c.ellipse(
            cx + dx - foot_w / 2, cy - body_h / 2 - foot_h * 0.6,
            cx + dx + foot_w / 2, cy - body_h / 2 + foot_h * 0.4,
            fill=1, stroke=0,
        )

    # Ear tufts.
    tuft_h = 6 * mm * scale
    base_y = cy + body_h * 0.42
    c.setFillColor(OWL_PURPLE_DARK)
    for side in (-1, 1):
        p = c.beginPath()
        p.moveTo(cx + side * body_w * 0.32, base_y)
        p.lineTo(cx + side * body_w * 0.18, base_y + tuft_h)
        p.lineTo(cx + side * body_w * 0.05, base_y)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    # Body.
    c.setFillColor(OWL_PURPLE)
    c.ellipse(cx - body_w / 2, cy - body_h / 2, cx + body_w / 2, cy + body_h / 2, fill=1, stroke=0)

    # Tummy.
    tummy_w, tummy_h = body_w * 0.6, body_h * 0.58
    c.setFillColor(OWL_PINK)
    c.ellipse(
        cx - tummy_w / 2, cy - body_h * 0.4,
        cx + tummy_w / 2, cy - body_h * 0.4 + tummy_h,
        fill=1, stroke=0,
    )

    # Eyes (white, with black pupils).
    eye_r = body_w * 0.22
    eye_dx = body_w * 0.24
    eye_cy = cy + body_h * 0.14
    c.setFillColor(colors.white)
    c.circle(cx - eye_dx, eye_cy, eye_r, fill=1, stroke=0)
    c.circle(cx + eye_dx, eye_cy, eye_r, fill=1, stroke=0)
    c.setFillColor(INK)
    pupil_r = eye_r * 0.45
    c.circle(cx - eye_dx, eye_cy, pupil_r, fill=1, stroke=0)
    c.circle(cx + eye_dx, eye_cy, pupil_r, fill=1, stroke=0)

    # Beak.
    beak_h = body_h * 0.12
    c.setFillColor(OWL_YELLOW)
    p = c.beginPath()
    p.moveTo(cx - body_w * 0.06, eye_cy - eye_r * 0.5)
    p.lineTo(cx + body_w * 0.06, eye_cy - eye_r * 0.5)
    p.lineTo(cx, eye_cy - eye_r * 0.5 - beak_h)
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def _draw_balloon(
    c: canvas.Canvas, cx: float, cy: float, color, w: float = 10 * mm, h: float = 13 * mm
) -> None:
    """A balloon with a small highlight, a knot, and a curly string."""
    c.setFillColor(color)
    c.ellipse(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=1, stroke=0)

    c.setFillColor(colors.white)
    hl_w, hl_h = w * 0.28, h * 0.2
    c.ellipse(cx - w * 0.22, cy + h * 0.12, cx - w * 0.22 + hl_w, cy + h * 0.12 + hl_h, fill=1, stroke=0)

    knot_y = cy - h / 2
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(cx - 1.2 * mm, knot_y)
    p.lineTo(cx + 1.2 * mm, knot_y)
    p.lineTo(cx, knot_y - 2 * mm)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    c.setStrokeColor(OWL_STRING_GRAY)
    c.setLineWidth(0.6)
    string_len = 14 * mm
    start_x, start_y = cx, knot_y - 2 * mm
    p2 = c.beginPath()
    p2.moveTo(start_x, start_y)
    p2.curveTo(
        start_x - 3 * mm, start_y - string_len * 0.33,
        start_x + 3 * mm, start_y - string_len * 0.66,
        start_x, start_y - string_len,
    )
    c.drawPath(p2, fill=0, stroke=1)


def _draw_header(c: canvas.Canvas, title: str, subtitle: str) -> float:
    """Draw the sky-blue header band with clouds, an owl mascot and
    balloons, then the title/subtitle/brand text on top. Returns the
    header's height."""
    header_top = PAGE_H
    header_bottom = PAGE_H - HEADER_H
    c.setFillColor(SKY_BLUE)
    c.rect(0, header_bottom, PAGE_W, HEADER_H, fill=1, stroke=0)

    for dx in (70 * mm, 118 * mm):
        _draw_cloud(c, MARGIN + dx, header_top - 8 * mm)
    _draw_cloud(c, PAGE_W - MARGIN - 16 * mm, header_top - 9 * mm, w=13 * mm)

    _draw_owl(c, MARGIN + 16 * mm, header_bottom + 15 * mm)

    for i, (dx, dy) in enumerate([(-32 * mm, 22 * mm), (-21 * mm, 18 * mm), (-10 * mm, 25 * mm)]):
        _draw_balloon(
            c, PAGE_W - MARGIN + dx, header_bottom + dy, BALLOON_COLORS[i % len(BALLOON_COLORS)]
        )

    c.setFillColor(OWL_PURPLE_DARK)
    c.setFont("Helvetica-Bold", 19)
    c.drawString(MARGIN + 36 * mm, header_top - 15 * mm, title)
    c.setFillColor(INK)
    c.setFont("Helvetica", 10.5)
    c.drawString(MARGIN + 36 * mm, header_top - 22 * mm, subtitle)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN + 36 * mm, header_top - 8 * mm, "Learn with Masti")

    return HEADER_H


def _draw_grass_strip(c: canvas.Canvas, top_y: float) -> float:
    """A green strip with a few triangular grass blades along its top edge.
    Returns the y cursor below it."""
    c.setFillColor(GRASS_GREEN)
    c.rect(0, top_y - GRASS_H, PAGE_W, GRASS_H, fill=1, stroke=0)

    blade_w = 5 * mm
    x = 3 * mm
    dark = False
    while x < PAGE_W - 3 * mm:
        c.setFillColor(GRASS_GREEN_DARK if dark else GRASS_GREEN)
        p = c.beginPath()
        p.moveTo(x, top_y - GRASS_H)
        p.lineTo(x + blade_w / 2, top_y - GRASS_H + 3 * mm)
        p.lineTo(x + blade_w, top_y - GRASS_H)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        x += blade_w * 1.4
        dark = not dark
    return top_y - GRASS_H


def _draw_name_date_stars_box(c: canvas.Canvas, top_y: float) -> float:
    """A cream rounded box with Name/Date blanks and 3 outline stars the
    child can colour in. Returns the y cursor below it."""
    box_h = 16 * mm
    c.setFillColor(CREAM)
    c.setStrokeColor(CREAM_BORDER)
    c.setLineWidth(1)
    c.roundRect(MARGIN, top_y - box_h, PAGE_W - 2 * MARGIN, box_h, radius=4 * mm, fill=1, stroke=1)

    text_y = top_y - box_h * 0.58
    x = MARGIN + 6 * mm
    c.setFont("Helvetica", 11)
    for label, blank_w in (("Name:", 45 * mm), ("Date:", 30 * mm)):
        c.setFillColor(INK)
        c.drawString(x, text_y, label)
        line_x0 = x + c.stringWidth(label, "Helvetica", 11) + 2 * mm
        line_x1 = line_x0 + blank_w
        c.setStrokeColor(INK)
        c.setLineWidth(0.6)
        c.line(line_x0, text_y - 1 * mm, line_x1, text_y - 1 * mm)
        x = line_x1 + 8 * mm

    c.setFillColor(INK)
    c.setFont("Helvetica", 11)
    c.drawString(x, text_y, "Stars:")
    star_x = x + c.stringWidth("Stars:", "Helvetica", 11) + 7 * mm
    for i in range(3):
        _draw_star(c, star_x + i * 10 * mm, text_y + 1.5 * mm, 4 * mm, STAR_OUTLINE)

    return top_y - box_h


def _draw_sum_box(c: canvas.Canvas, x: float, y: float, w: float, h: float, index: int, s: ColumnSum) -> None:
    fill_color, accent = PASTELS[(index - 1) % len(PASTELS)]
    c.setFillColor(fill_color)
    c.roundRect(x, y, w, h, radius=2.5 * mm, fill=1, stroke=0)

    badge_r = 3.2 * mm
    badge_cx, badge_cy = x + 5 * mm, y + h - 5 * mm
    c.setFillColor(accent)
    c.circle(badge_cx, badge_cy, badge_r, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(badge_cx, badge_cy - 2.4, str(index))

    right_x = x + w - 4 * mm
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(right_x, y + h - 9 * mm, str(s.a))
    c.drawRightString(right_x, y + h - 15 * mm, f"{s.op} {s.b}")

    rule_y = y + h - 17 * mm
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line(x + 4 * mm, rule_y, x + w - 4 * mm, rule_y)

    # Working line for the student to write their answer/working on.
    c.setStrokeColor(accent)
    c.setLineWidth(1)
    c.line(x + 4 * mm, y + 4 * mm, x + w - 4 * mm, y + 4 * mm)


def _draw_sum_grid(c: canvas.Canvas, top_y: float, sums: list[ColumnSum]) -> float:
    """Draw the 5-column grid of sums starting below `top_y`. Returns the
    y cursor below the grid."""
    cols = GRID_COLUMNS
    gutter = 4 * mm
    box_w = (PAGE_W - 2 * MARGIN - gutter * (cols - 1)) / cols
    box_h = 24 * mm

    for i, s in enumerate(sums):
        col, row = i % cols, i // cols
        x = MARGIN + col * (box_w + gutter)
        y = top_y - (row + 1) * box_h - row * gutter
        _draw_sum_box(c, x, y, box_w, box_h, i + 1, s)

    rows = -(-len(sums) // cols)  # ceil division
    return top_y - rows * box_h - (rows - 1) * gutter


def _draw_story_problems_banner(c: canvas.Canvas, top_y: float) -> float:
    banner_h = 8 * mm
    c.setFillColor(BANNER_COLOR)
    c.roundRect(MARGIN, top_y - banner_h, PAGE_W - 2 * MARGIN, banner_h, radius=3 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_W / 2, top_y - banner_h * 0.68, "Story Problems - can you solve them?")
    return top_y - banner_h


def _draw_word_problem_cards(
    c: canvas.Canvas, top_y: float, word_problems: list[WordProblem], start_index: int
) -> float:
    """Draw each word problem in its own pastel rounded card, with an
    Answer line inside. Returns the y cursor below the last card."""
    text_x = MARGIN + 14 * mm
    max_text_w = PAGE_W - MARGIN - text_x - 4 * mm
    y = top_y
    for i, wp in enumerate(word_problems, start=start_index):
        fill_color, accent = PASTELS[(i - 1) % len(PASTELS)]
        lines = simpleSplit(wp.text, "Helvetica", 10, max_text_w)
        card_h = 6 * mm + len(lines) * 5 * mm + 6 * mm

        c.setFillColor(fill_color)
        c.roundRect(MARGIN, y - card_h, PAGE_W - 2 * MARGIN, card_h, radius=3 * mm, fill=1, stroke=0)

        badge_r = 3.2 * mm
        badge_cx, badge_cy = MARGIN + 7 * mm, y - 6 * mm
        c.setFillColor(accent)
        c.circle(badge_cx, badge_cy, badge_r, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(badge_cx, badge_cy - 2.4, str(i))

        ty = y - 6 * mm
        c.setFillColor(INK)
        c.setFont("Helvetica", 10)
        for line in lines:
            c.drawString(text_x, ty, line)
            ty -= 5 * mm

        c.drawString(text_x, ty - 1 * mm, "Answer:")
        c.setStrokeColor(accent)
        c.setLineWidth(1)
        c.line(text_x + 16 * mm, ty - 1.5 * mm, PAGE_W - MARGIN - 6 * mm, ty - 1.5 * mm)

        y -= card_h + 4 * mm
    return y


def _draw_footer(c: canvas.Canvas, message: str = "You can do it! Take your time.") -> None:
    c.setFillColor(FOOTER_GREEN)
    c.rect(0, 0, PAGE_W, 10 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(PAGE_W / 2, 3.6 * mm, message)


def _draw_answer_grid(
    c: canvas.Canvas, top_y: float, answers: list[int], start_index: int
) -> float:
    """Draw a 5-column grid of "N. answer" entries. Returns the y cursor
    below the grid."""
    cols = GRID_COLUMNS
    gutter_x, gutter_y = 6 * mm, 8 * mm
    col_w = (PAGE_W - 2 * MARGIN - gutter_x * (cols - 1)) / cols
    row_h = 9 * mm

    c.setFillColor(INK)
    c.setFont("Helvetica", 10)
    for i, answer in enumerate(answers):
        col, row = i % cols, i // cols
        x = MARGIN + col * (col_w + gutter_x)
        y = top_y - (row + 1) * row_h - row * gutter_y
        c.drawString(x, y, f"{start_index + i}. {answer}")

    rows = -(-len(answers) // cols)
    return top_y - rows * row_h - (rows - 1) * gutter_y


def _draw_answer_key_closer(c: canvas.Canvas, top_y: float) -> None:
    """The little celebration scene at the end of the answer key: the owl
    mascot, two balloons, and an encouraging line."""
    _draw_owl(c, MARGIN + 14 * mm, top_y - 11 * mm, scale=0.55)
    _draw_balloon(c, PAGE_W - MARGIN - 22 * mm, top_y - 9 * mm, BALLOON_COLORS[0], w=8 * mm, h=10 * mm)
    _draw_balloon(c, PAGE_W - MARGIN - 11 * mm, top_y - 13 * mm, BALLOON_COLORS[1], w=8 * mm, h=10 * mm)
    c.setFillColor(OWL_PURPLE_DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_W / 2, top_y - 13 * mm, "Great work! Colour a star for every correct answer.")


def render_worksheet_pdf(data: WorksheetData, set_label: str, out_path: Path) -> None:
    """Render `data` as a 2-page PDF: a questions page followed by an
    answer-key page, both branded with the same playful header/footer."""
    title = TOPIC_TITLES[data.topic]
    subtitle = f"Class 3 - {set_label}"
    c = canvas.Canvas(str(out_path), pagesize=A4)

    # --- Page 1: questions ---
    header_h = _draw_header(c, title, subtitle)
    y = _draw_grass_strip(c, PAGE_H - header_h)
    y = _draw_name_date_stars_box(c, y) - 4 * mm
    y = _draw_sum_grid(c, y, data.sums) - 6 * mm
    y = _draw_story_problems_banner(c, y) - 4 * mm
    _draw_word_problem_cards(c, y, data.word_problems, start_index=len(data.sums) + 1)
    _draw_footer(c)
    c.showPage()

    # --- Page 2: answer key (no Name/Date/Stars row) ---
    header_h = _draw_header(c, f"{title} - Answer Key", subtitle)
    y = _draw_grass_strip(c, PAGE_H - header_h) - 10 * mm

    c.setFillColor(HEADING_PURPLE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, y, "Sums")
    y -= 8 * mm
    y = _draw_answer_grid(c, y, [s.answer for s in data.sums], start_index=1) - 12 * mm

    c.setFillColor(HEADING_PURPLE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, y, "Word Problems")
    y -= 8 * mm
    y = _draw_answer_grid(
        c, y, [wp.answer for wp in data.word_problems], start_index=len(data.sums) + 1
    )
    _draw_answer_key_closer(c, y - 14 * mm)
    _draw_footer(c)
    c.showPage()

    c.save()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate a print-ready Class 3 Maths worksheet PDF")
    parser.add_argument("--topic", required=True, choices=sorted(TOPIC_TITLES), help="Maths topic")
    parser.add_argument(
        "--set", dest="set_label", required=True, help='Set label shown in the subtitle, e.g. "Set A"'
    )
    parser.add_argument("--seed", type=int, default=0, help="Random seed for reproducible variation")
    parser.add_argument("--out", required=True, help="Output PDF path")
    args = parser.parse_args(argv)

    data = generate_worksheet_data(args.topic, args.seed)
    out_path = Path(args.out)
    render_worksheet_pdf(data, args.set_label, out_path)
    print(f"Wrote {out_path} ({len(data.sums)} sums, {len(data.word_problems)} word problems)")


if __name__ == "__main__":
    main()
