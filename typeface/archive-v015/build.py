"""New Orkhon 0.14: speculative uppercase and lowercase serif forms."""

import math
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from shapely import affinity, set_precision
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from ductus import em_print_path
from lowercase import AQ_PATHS, AQ_SERIFS, LOWER, Lower

ROOT = Path(__file__).resolve().parent
VERSION = "0.15"
FONT_VERSION = "0.915"
EM_I_LIGATURES = ("u10C22_u10C03.liga", "u10C22_u10C03.lc.liga")
HEIGHT, OVERSHOOT = 700, 10
STEM, HAIRLINE = 90, 64
ARM_TOP, ARM_BOTTOM = HEIGHT - HAIRLINE // 2, HAIRLINE // 2
SIDES = {"stem": 55, "round": 32, "diagonal": 26, "open": 18, "lambda": 8}
FORK_RETURNS = (
    "M 90 700 L 90 535 C 90 405 255 405 255 535 L 255 700 "
    "L 255 535 C 255 405 420 405 420 535 L 475 700"
)
FORK_POLE = "M 475 700 L 475 0"
FORK_SERIFS = [(90, 700, -1), (255, 700, -1), (475, 700, -1), (475, 0, 1)]
Y_STROKES = ["M 80 700 L 270 335 L 270 0", "M 460 700 L 270 335"]
Y_SERIFS = [(80, 700, -1), (460, 700, -1), (270, 0, 1)]


@dataclass
class Letter:
    code: int
    paths: list[str]
    serifs: list[tuple[int, int, int]]
    sides: tuple[str, str]
    decision: str
    round_top: bool = False
    round_bottom: bool = False
    dots: tuple = ()
    rule: str = "1,3,4,5,6"
    reliefs: tuple[tuple[int, float, float, float, float], ...] = ()
    stroke_join: str = "round"
    stroke_stem: int = STEM
    stroke_hair: int = HAIRLINE
    ink_zone: bool = False


LETTERS = [
    Letter(0x10C00, [
        f"M 470 {ARM_TOP - 72} L 470 {ARM_TOP} L 100 {ARM_TOP} "
        f"L 470 {ARM_BOTTOM} L 100 {ARM_BOTTOM} L 100 {ARM_BOTTOM + 72}",
    ], [(100, 700, -1), (470, 0, 1)], ("diagonal", "diagonal"),
        "Opposed level arms meet a long incline. Optical bars and paired serifs keep the mirrored Z legible at text sizes."),
    Letter(0x10C03, [
        f"M 125 0 L 125 {ARM_TOP} L 440 {ARM_TOP} L 440 {ARM_TOP - 72}",
    ], [(125, 0, 1)], ("stem", "open"),
        "The upper return levels into the same cap arm as A; its upright remains the diagnostic difference."),
    Letter(0x10C06, [
        "M 130 700 C 130 555 175 445 315 350 C 155 270 115 135 130 0",
    ], [], ("round", "open"), "One flowing cusp; equal-height terminals, no ragged offset seam."),
    Letter(0x10C07, [
        "M 130 0 L 130 700 C 240 700 280 365 405 350 L 405 700",
    ], [(130, 0, 1), (405, 700, -1)], ("stem", "stem"),
        "A shared shoulder connects opposed posts; side spaces follow the stem class."),
    Letter(0x10C09, [
        "M 230 700 C 105 610 185 530 295 440 C 460 300 390 0 235 0 C 60 0 55 245 115 335",
    ], [], ("round", "round"), "Return and bowl meet continuously; the bowl receives a full text-height silhouette.",
        round_bottom=True),
    Letter(0x10C0B, [
        "M 250 700 C 80 635 95 430 250 365 C 405 430 420 635 250 700",
        "M 250 365 L 105 0", "M 250 365 L 395 0",
    ], [(105, 0, 1), (395, 0, 1)], ("diagonal", "diagonal"),
        "The eye has a clear counter; the two legs use the same diagonal vocabulary."),
    Letter(0x10C0D, [
        "M 90 700 C 290 620 290 475 90 400",
        "M 530 700 C 330 620 330 475 530 400",
        "M 310 290 L 310 0",
    ], [(310, 0, 1)], ("open", "open"),
        "The uppercase preserves two separate opposed horns and a third detached lower staff."),
    Letter(0x10C0F, [
        "M 495 580 C 425 670 320 685 255 655 C 45 600 45 100 255 45 "
        "C 320 15 425 30 495 120",
        "M 490 350 L 105 350",
    ], [], ("round", "open"),
        "A rounded, mirrored Cyrillic-э construction: open to the right, with a bar reaching into the left bowl.",
        round_top=True, round_bottom=True),
    Letter(0x10C11, [
        "M 95 700 C 300 625 300 440 95 350 C 300 265 300 75 95 0",
        "M 355 700 C 560 625 560 440 355 350 C 560 265 560 75 355 0",
    ], [], ("open", "round"), "Twin serpentine strokes have matching turns and a deliberately open channel."),
    Letter(0x10C13, [
        "M 100 700 C 190 505 340 195 430 0",
        "M 430 700 C 340 505 190 195 100 0",
    ], [(100, 0, 1), (430, 0, 1)], ("diagonal", "diagonal"),
        "The cross uses balanced opposing diagonals, not unequal corner artifacts."),
    Letter(0x10C14, [
        "M 200 700 L 435 0",
        "M 200 700 C 225 555 320 455 420 455 C 510 455 550 560 550 700 "
        "L 550 355 C 540 270 445 255 317.5 350",
        "M 95 0 L 95 210 C 95 330 220 420 317.5 350",
    ], [(95, 0, 1), (200, 700, -1), (435, 0, 1), (550, 700, -1)],
        ("stem", "stem"),
        "Merge the upper-reaching pole and right post with a rounded cup; a lower return meets the slanted pole at mid-height."),
    Letter(0x10C16, [
        "M 120 15 L 120 685 C 560 685 560 15 120 15",
    ], [(120, 0, 1), (120, 700, -1)], ("stem", "round"),
        "The bowl shares the oval's counter width and the common full-height text body."),
    Letter(0x10C18, [
        "M 120 395 C -15 820 525 820 405 425 C 370 305 250 285 250 130 L 250 0",
    ], [(250, 0, 1)], ("round", "round"),
        "An open head and descending hook with one clean, continuous outline.", round_top=True),
    Letter(0x10C1A, [
        "M 400 0 L 400 700",
        "M 400 668 C 45 720 45 350 400 350",
    ], [(400, 0, 1), (400, 700, -1)], ("round", "stem"),
        "The two arms close into an upper bowl: a reversed P, structurally distinct from EP's open head."),
    Letter(0x10C1C, [
        f"M 125 0 L 125 {ARM_TOP} L 420 {ARM_TOP} L 420 {ARM_TOP - 72}",
        "M 125 350 C 260 390 375 370 375 250 L 375 0",
    ], [(125, 0, 1), (375, 0, 1)], ("stem", "open"),
        "The cap arm follows I; a lower shoulder retains the two-tier distinction."),
    Letter(0x10C1E, [
        f"M 365 700 L 365 {ARM_BOTTOM} L 95 {ARM_BOTTOM} L 95 {ARM_BOTTOM + 72}",
    ], [(365, 700, -1)], ("open", "stem"),
        "Level the bottom return, matching A's lower arm but retaining the upright."),
    Letter(0x10C20, Y_STROKES, Y_SERIFS, ("diagonal", "diagonal"),
        "A Latin-like Y: two straight upper arms, one lower stem and shared cap/foot serifs."),
    Letter(0x10C21, [
        "M 115 0 L 115 685 C 215 685 230 420 300 405 C 370 420 385 685 485 685 L 485 0",
    ], [(115, 0, 1), (485, 0, 1)], ("stem", "stem"),
        "Two equal posts frame a smooth valley; both feet and shoulders follow the shared system."),
    Letter(0x10C22, [em_print_path()], [(475, 0, 1)], ("open", "round"),
        "An authored one-stroke bowl-and-leg route, like R without its upright; smoothing alone cannot derive it."),
    Letter(0x10C23, [
        "M 105 605 C 125 660 190 685 270 685 C 575 685 575 15 270 15 C 190 15 125 40 105 95",
    ], [], ("open", "round"),
        "A full open bowl, like reversed C, with inward returns instead of a parenthesis.",
        round_top=True, round_bottom=True),
    Letter(0x10C24, [
        "M 80 0 L 80 700", "M 80 700 L 450 0", "M 450 0 L 450 700",
    ], [(80, 0, 1), (80, 700, -1), (450, 0, 1), (450, 700, -1)],
        ("stem", "stem"),
        "A single N replaces the crowded double N; no other current sign uses that construction."),
    Letter(0x10C26, [
        "M 110 700 L 110 310 C 110 45 190 0 300 0 C 410 0 490 45 490 310 L 490 700",
    ], [(110, 700, -1), (490, 700, -1)], ("stem", "stem"),
        "An ordinary rounded u with two upright stems; remove its three inherited dots in this proposed reform.",
        round_bottom=True),
    Letter(0x10C28, [
        "M 110 0 L 110 700",
        "M 110 700 C 400 700 465 550 360 445 C 325 405 210 385 110 370",
        "M 110 370 C 475 355 500 160 390 65 C 335 15 210 0 110 0",
    ], [(110, 0, 1), (110, 700, -1)], ("stem", "round"),
        "Two wider bowls open the counters; keep the common upright and full stroke model."),
    Letter(0x10C2A, [
        "M 105 605 C 130 660 190 685 270 685 C 545 685 545 350 230 350 "
        "C 545 350 545 15 270 15 C 190 15 130 40 105 95",
    ], [], ("open", "round"),
        "The middle notch becomes a waist between two open bowls, like Western 3.",
        round_top=True, round_bottom=True),
    Letter(0x10C2D, [
        "M 285 700 L 285 0", "M 285 350 C 205 350 150 440 95 460",
    ], [(285, 0, 1), (285, 700, -1)], ("open", "stem"),
        "The mid-stem branch stays distinct from a bottom return without using a different cap height."),
    Letter(0x10C2F, [
        f"M 380 0 L 380 {ARM_TOP} L 100 {ARM_TOP} L 100 {ARM_TOP - 72}",
    ], [(380, 0, 1)], ("open", "stem"),
        "A mirrored cap arm shares the I/A family's return, without the second k arm."),
    Letter(0x10C30, [
        "M 125 700 L 125 0",
        "M 125 540 C 245 565 310 685 390 685 L 390 500",
        "M 125 230 C 245 255 310 370 390 370 L 390 0",
    ], [(125, 0, 1), (390, 0, 1), (125, 700, -1)], ("stem", "stem"),
        "Two tiers and short end stems share a standard shoulder and an open lower counter."),
    Letter(0x10C31, [FORK_RETURNS, FORK_POLE], FORK_SERIFS, ("open", "stem"),
        "A Latinized mirrored Arabic 3; taper the incoming last return where it meets the unchanged straight pole.",
        reliefs=((0, 445, 515, 135, .45),)),
    Letter(0x10C32, [
        "M 60 0 L 262.5 700 L 465 0",
    ], [(60, 0, 1), (465, 0, 1)], ("diagonal", "diagonal"),
        "Capital Greek-lambda construction: two straight rising legs share one pointed apex, with baseline serifs and no curved head.",
        stroke_join="mitre"),
    Letter(0x10C34, AQ_PATHS, AQ_SERIFS, ("open", "stem"),
        "A low curling free leg distinguishes q from the upturned r; counter widths are related."),
    Letter(0x10C36, [
        "M 365 685 C 245 675 130 490 85 350 C 130 210 245 25 365 15 L 365 685",
    ], [(365, 0, 1), (365, 700, -1)], ("diagonal", "stem"),
        "The rounded triangle shares full height with the round bowl but preserves its pointed side."),
    Letter(0x10C38, [
        "M 265 700 L 265 0",
        "M 75 285 C 170 285 235 165 265 0 C 295 165 360 285 455 285",
    ], [(265, 700, -1)], ("open", "open"),
        "Retain the upright anchor construction; taper only the incoming wings at the pole.",
        reliefs=((1, 265, 180, 210, .35),)),
    Letter(0x10C3A, [
        "M 380 0 L 380 700",
        "M 380 350 C 275 350 205 205 100 160 C 185 325 175 530 100 630",
    ], [(380, 0, 1), (380, 700, -1)], ("open", "stem"),
        "The free leg turns upward; a related counter and equal stem keep the q/r family coherent."),
    Letter(0x10C3C, [
        "M 280 0 L 280 545",
        "M 70 560 C 110 560 110 685 170 685 C 220 685 225 560 280 545 C 335 560 340 685 390 685 C 450 685 450 560 490 560",
    ], [(280, 0, 1)], ("open", "open"),
        "Two equal shoulders meet above the stem. The stem ends at the valley, never above the roof."),
    Letter(0x10C3D, [
        "M 120 700 L 120 525 C 120 400 475 400 475 525 L 475 700",
        "M 475 700 L 475 0",
    ], [(120, 700, -1), (475, 700, -1), (475, 0, 1)], ("open", "stem"),
        "One rounded upper return feeds a straight pole; IC has two returns and a third upper tip."),
    Letter(0x10C3E, [
        "M 150 0 L 150 700",
    ], [(150, 0, 1), (150, 700, -1)], ("stem", "stem"),
        "The minim uses the same height and stem as the rest; width comes from its two fitted side spaces."),
    Letter(0x10C3F, [
        "M 275 700 C 25 700 25 0 275 0 C 525 0 525 700 275 700",
    ], [], ("round", "round"),
        "The oval is the reference for round counters and round-to-round spacing.",
        round_top=True, round_bottom=True),
    Letter(0x10C41, [
        "M 270 0 L 270 300 L 100 668 C 190 700 350 700 440 668 L 270 300",
    ], [(270, 0, 1)], ("diagonal", "diagonal"),
        "Raise the fork's link to close its head; retain two branches and one stem, not a third upper prong."),
    Letter(0x10C43, [
        "M 125 0 L 125 700",
        "M -20 668 L 440 668",
        "M 125 560 C 545 600 545 -5 125 32",
    ], [(125, 0, 1)], ("stem", "round"),
        "The roof becomes an overhanging top arm; the eye moves right of the staff as one broad bowl, breaking the old symmetry."),
    Letter(0x10C45, [
        "M 125 0 L 125 700",
        "M 125 340 C 245 340 325 520 410 520 C 340 365 365 125 450 0",
    ], [(125, 0, 1), (125, 700, -1)], ("stem", "open"),
        "The falling leg follows the same shoulder tension and lower counter scale as the other branched stems."),
    Letter(0x10C47, [
        "M 105 0 L 105 335 C 105 525 165 620 300 620 "
        "C 435 620 495 525 495 335 L 495 0",
        "M 210 700 C 245 655 275 630 300 620 C 325 630 355 655 390 700",
    ], [(105, 0, 1), (495, 0, 1)], ("stem", "stem"),
        "Two straight sides support an inverted u; two symmetric rounded hat prongs meet at the roof, not through it."),
    Letter(0x10C48, [
        "M 300 350 C -20 465 60 668 300 668 C 540 668 620 465 300 350 "
        "C 36 255 -12 32 300 32 C 612 32 564 255 300 350",
    ], [], ("round", "round"),
        "An uninterrupted figure-eight route replaces the post-and-diagonal weave; two stacked counters open the waist."),
]


def points(path: str) -> list[tuple[float, float]]:
    pen = RecordingPen()
    parse_path(path, pen)
    result: list[tuple[float, float]] = []
    current: tuple[float, float] | None = None
    for op, values in pen.value:
        if op == "moveTo":
            if result:
                raise ValueError("Use a separate path for each contour.")
            current = (float(values[0][0]), float(values[0][1]))
            result.append(current)
        elif op == "lineTo":
            assert current is not None, "A line must follow a move."
            target = values[0]
            n = max(2, math.ceil(math.dist(current, target) / 3))
            result.extend((current[0] + (target[0] - current[0]) * i / n,
                           current[1] + (target[1] - current[1]) * i / n)
                          for i in range(1, n + 1))
            current = target
        elif op == "curveTo":
            assert current is not None, "A curve must follow a move."
            a, b, c = values
            n = max(24, math.ceil((math.dist(current, a) + math.dist(a, b)
                                  + math.dist(b, c)) / 3))
            for i in range(1, n + 1):
                t, s = i / n, 1 - i / n
                result.append((
                    s**3 * current[0] + 3*s*s*t*a[0] + 3*s*t*t*b[0] + t**3*c[0],
                    s**3 * current[1] + 3*s*s*t*a[1] + 3*s*t*t*b[1] + t**3*c[1],
                ))
            current = c
        elif op not in ("endPath", "closePath"):
            raise ValueError(op)
    return result


def stroke(path, stem=STEM, hair=HAIRLINE, reliefs=(), join_style="round"):
    samples = points(path)
    line = LineString(samples)
    normalized = affinity.scale(line, 2 / stem, 2 / hair, origin=(0, 0))
    closed = line.is_closed
    regular = normalized.buffer(1, cap_style="round" if closed else "flat",
                                join_style=join_style, quad_segs=12)
    if not reliefs:
        shape = regular
    else:
        # Taper the incoming stroke, not the shared upright or the whole glyph.
        coords = list(normalized.coords)
        widths = []
        for point in samples:
            width = 1.
            for x, y, radius, minimum in reliefs:
                distance = math.dist(point, (x, y))
                if distance < radius:
                    blend = (1 + math.cos(math.pi * distance / radius)) / 2
                    width = min(width, 1 - (1 - minimum) * blend)
            widths.append(width)
        pieces = []
        for i, (a, b) in enumerate(zip(coords, coords[1:], strict=False)):
            length = math.dist(a, b)
            if length == 0:
                continue
            nx, ny = -(b[1] - a[1]) / length, (b[0] - a[0]) / length
            wa, wb = widths[i], widths[i + 1]
            pieces.append(Polygon([
                (a[0] + nx * wa, a[1] + ny * wa),
                (b[0] + nx * wb, b[1] + ny * wb),
                (b[0] - nx * wb, b[1] - ny * wb),
                (a[0] - nx * wa, a[1] - ny * wa),
            ]))
        indices = range(len(coords)) if closed else range(1, len(coords) - 1)
        pieces.extend(Point(coords[i]).buffer(widths[i], quad_segs=12) for i in indices)
        shape = unary_union(pieces).intersection(regular)
    return affinity.scale(shape, stem / 2, hair / 2, origin=(0, 0))


def foot(x, y, direction, stem=STEM):
    half = stem / 2
    tip = half + 30
    return Polygon([
        (x - tip, y), (x + tip, y), (x + tip, y + direction * 20),
        (x + half + 13, y + direction * 24), (x + half + 5, y + direction * 42),
        (x + half, y + direction * 58), (x - half, y + direction * 58),
        (x - half - 5, y + direction * 42), (x - half - 13, y + direction * 24),
        (x - tip, y + direction * 20),
    ])


def leg_section(samples, x, y, height, stem, hair):
    """Horizontal centre and half-width of an elliptical-pen leg at a height."""
    target = y + height
    best = None
    for a, b in zip(samples, samples[1:], strict=False):
        if (a[1] - target) * (b[1] - target) > 0 or a[1] == b[1]:
            continue
        t = (target - a[1]) / (b[1] - a[1])
        px = a[0] + t * (b[0] - a[0])
        if best is None or abs(px - x) < abs(best[0] - x):
            best = (px, b[0] - a[0], b[1] - a[1])
    assert best is not None and abs(best[0] - x) < 150
    px, dx, dy = best
    length = math.hypot(dx, dy)
    u, v = dx / length, dy / length
    return px, math.sqrt((stem / 2) ** 2 * v * v + (hair / 2) ** 2 * u * u) / abs(v)


def leg_foot(path, x, y, direction, stem=STEM, hair=HAIRLINE):
    """A bracketed serif whose upper corners follow a tilted leg.

    Returns None when the path does not end here, and "upright" when the
    standard foot already fits the leg.
    """
    samples = points(path)
    if math.dist(samples[-1], (x, y)) < 1:
        samples = samples[::-1]
    if math.dist(samples[0], (x, y)) >= 1:
        return None
    near = next((p for p in samples if math.dist(p, (x, y)) >= 12), samples[-1])
    if abs(near[1] - y) < math.dist(near, (x, y)) * .5:
        return "upright"
    reach = next((p for p in samples if abs(p[1] - y) >= 58), samples[-1])
    dx, dy = reach[0] - x, reach[1] - y
    if dy * direction <= 0 or abs(dx) < .5 or abs(dy) < math.hypot(dx, dy) * .5:
        return "upright"
    # Extend the end tangent below the terminal so h=0 is measured on the leg, not its cap.
    lead = (x - dx / math.hypot(dx, dy) * 30, y - dy / math.hypot(dx, dy) * 30)
    samples = [lead, *samples]
    rows = []
    spread = max(30, abs(dx / dy) * 31)
    for h in range(0, 59, 2):
        grow = spread * (1 - h / 58) ** 2
        rows.append((h, grow, *leg_section(samples, x, y, direction * h, stem, hair)))
    right = [(c + w + grow, y + direction * h) for h, grow, c, w in rows]
    left = [(c - w - grow, y + direction * h) for h, grow, c, w in rows]
    return Polygon([*right, *left[::-1]])


def serif(letter, x, y, direction, stem, hair):
    feet = [leg_foot(path, x, y, direction, stem, hair) for path in letter.paths]
    feet = [shape for shape in feet if shape is not None]
    if not feet or any(isinstance(shape, str) for shape in feet):
        return foot(x, y, direction, stem)
    return unary_union(feet)


def constructed(letter):
    stem = getattr(letter, "stroke_stem", STEM)
    hair = getattr(letter, "stroke_hair", HAIRLINE)
    base = getattr(letter, "bottom", 0)
    cap = getattr(letter, "top", HEIGHT)
    shape = unary_union([
        *(stroke(p, stem, hair, [r[1:] for r in letter.reliefs if r[0] == i],
                 join_style=getattr(letter, "stroke_join", "round"))
          for i, p in enumerate(letter.paths)),
        *(serif(letter, x, y, direction, stem, hair) for x, y, direction in letter.serifs),
        *(Point(x, y).buffer(r, quad_segs=24) for x, y, r in letter.dots),
    ]).simplify(.3, preserve_topology=True)
    assert shape.is_valid, f"Invalid outline U+{letter.code:05X}"
    # Baseline/cap serifs must meet a flat edge, even on an inclined stroke.
    ink_zone = getattr(letter, "ink_zone", False)
    clip_bottom = base if (
        (ink_zone and not letter.round_bottom)
        or any(y == base for _, y, _ in letter.serifs)
    ) else -2000
    clip_top = cap if (
        (ink_zone and not letter.round_top)
        or any(y == cap for _, y, _ in letter.serifs)
    ) else 2000
    shape = shape.intersection(box(-2000, clip_bottom, 2000, clip_top))
    return shape


def geometry(letter):
    shape = constructed(letter)
    base = getattr(letter, "bottom", 0)
    cap = getattr(letter, "top", HEIGHT)
    bottom = base - OVERSHOOT if letter.round_bottom else base
    top = cap + OVERSHOOT if letter.round_top else cap
    _, y0, _, y1 = shape.bounds
    shape = affinity.translate(shape, yoff=-y0)
    shape = affinity.scale(shape, yfact=(top - bottom) / (y1 - y0), origin=(0, 0))
    return affinity.translate(shape, yoff=bottom)


def fitted(letter, sidebearings=SIDES):
    shape = geometry(letter)
    x0, _, x1, _ = shape.bounds
    left, right = (sidebearings[side] for side in letter.sides)
    shape = affinity.translate(shape, xoff=left - x0)
    return shape, round(x1 - x0 + left + right)


def fitted_point(letter, x, y, sidebearings=SIDES):
    raw = constructed(letter)
    x0, y0, _, y1 = raw.bounds
    bottom = getattr(letter, "bottom", 0) - (OVERSHOOT if letter.round_bottom else 0)
    top = getattr(letter, "top", HEIGHT) + (OVERSHOOT if letter.round_top else 0)
    return x + sidebearings[letter.sides[0]] - x0, bottom + (y - y0) * (top - bottom) / (y1 - y0)


def al_kerning(shapes, advances, capital_forms=LETTERS, lower_forms=LOWER, sidebearings=SIDES):
    """Tuck a visual-left neighbor into AL only where its descender leaves room."""
    al = shapes["u10C1E.lc"]
    al_body = al.intersection(box(-2000, 0, 3000, 510))
    pairs = {}
    forms: list[Letter | Lower] = [*capital_forms, *lower_forms]
    for letter in forms:
        name = f"u{letter.code:05X}" + (".lc" if hasattr(letter, "top") else "")
        if name == "u10C1E.lc":
            continue
        neighbor = shapes[name]
        x0, _, x1, _ = neighbor.bounds
        right_bottom = box(x0 + (x1 - x0) * .65, -400, x1 + 10, -35)
        if neighbor.intersects(right_bottom):
            continue
        neighbor_body = neighbor.intersection(box(-2000, 0, 3000, 510))
        if neighbor_body.is_empty:
            continue
        target = max(65, sidebearings["open"] + sidebearings[letter.sides[1]] + 15)
        gap = al_body.distance(affinity.translate(neighbor_body, xoff=-advances[name]))
        limit = min(300, int(advances[name] * .6))
        amount = 10 * (max(0, min(limit, int(gap - target))) // 10)
        while amount >= 30:
            positioned = affinity.translate(al, xoff=advances[name] - amount)
            if positioned.distance(neighbor) >= 30:
                pairs[name] = amount
                break
            amount -= 10
    return pairs


def em_i_ligatures(shapes, advances, capital_forms=LETTERS, lower_forms=LOWER, sidebearings=SIDES):
    carets = {}
    variants: list[tuple[list[Letter] | list[Lower], str, str, int, int]] = [
        (capital_forms, "", EM_I_LIGATURES[0], 50, 700),
        (lower_forms, ".lc", EM_I_LIGATURES[1], 48, 510),
    ]
    for group, suffix, name, reduction, top in variants:
        source_i = next(g for g in group if g.code == 0x10C03)
        source_em = next(g for g in group if g.code == 0x10C22)
        if suffix:
            context_i = replace(source_i, paths=["M 105 -190 L 105 340 C 105 475 270 480 350 480"])
            p = fitted_point(context_i, 350, 480, sidebearings)
            q = fitted_point(source_em, 95, 480, sidebearings)
        else:
            arm_top = 700 - source_i.stroke_hair / 2
            context_i = replace(source_i, paths=[f"M 125 0 L 125 {arm_top} L 440 {arm_top}"])
            p = fitted_point(context_i, 440, arm_top, sidebearings)
            q = fitted_point(source_em, 100, 685, sidebearings)
        i_name, em_name = "u10C03" + suffix, "u10C22" + suffix
        left, _ = fitted(context_i, sidebearings)
        offset = advances[i_name] - reduction
        right = affinity.translate(shapes[em_name], xoff=offset)
        q = (q[0] + offset, q[1])
        span = q[0] - p[0]
        path = (f"M {p[0] - 8} {p[1]} "
                f"C {p[0] + span / 3} {p[1]} {q[0] - span / 3} {q[1]} {q[0] + 8} {q[1]}")
        parts = [left, right, stroke(path, source_i.stroke_stem, source_i.stroke_hair)]
        shape = unary_union(parts).intersection(box(-2000, -190 if suffix else 0, 3000, top))
        assert shape.geom_type == "Polygon" and shape.is_valid, name
        shapes[name] = set_precision(shape, grid_size=1).simplify(.3, preserve_topology=True)
        advances[name] = advances[i_name] + advances[em_name] - reduction
        carets[name] = advances[i_name] - reduction // 2
    return carets


def to_glyph(shape):
    pen = TTGlyphPen(None)
    polys = [shape] if shape.geom_type == "Polygon" else list(shape.geoms)
    for poly in polys:
        poly = orient(poly, sign=-1)
        for ring in [poly.exterior, *poly.interiors]:
            coords = [(round(x), round(y)) for x, y in ring.coords[:-1]]
            coords = [p for i, p in enumerate(coords) if i == 0 or p != coords[i-1]]
            if len(set(coords)) < 3:
                continue
            pen.moveTo(coords[0])
            for point in coords[1:]:
                pen.lineTo(point)
            pen.closePath()
    return pen.glyph()


def build_font(lowercase_default, style="serif"):
    if style == "sans":
        from sans import SANS_SIDES, sans_forms
        capital_forms, lower_forms = sans_forms(LETTERS, LOWER)
        sidebearings = SANS_SIDES
    elif style == "serif":
        capital_forms, lower_forms, sidebearings = LETTERS, LOWER, SIDES
    else:
        raise ValueError(style)
    names = [".notdef", "space", "divider", "period", "comma"]
    names += [f"u{g.code:05X}" for g in capital_forms]
    names += [f"u{g.code:05X}.lc" for g in lower_forms]
    names += list(EM_I_LIGATURES)
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(names)
    cmap = {32: "space", 0x205A: "divider", 46: "period", 44: "comma"}
    cmap.update({
        g.code: f"u{g.code:05X}{'.lc' if lowercase_default else ''}"
        for g in capital_forms
    })
    fb.setupCharacterMap(cmap)
    shapes = {
        ".notdef": Polygon([(80, 0), (80, 700), (480, 700), (480, 0)],
                            [[(120, 40), (440, 40), (440, 660), (120, 660)]]),
        "divider": unary_union([Point(135, y).buffer(28) for y in (230, 470)]),
        "period": Point(110, 30).buffer(30),
        "comma": stroke("M 125 70 C 170 -10 130 -70 85 -90"),
    }
    advances = {".notdef": 560, "space": 245, "divider": 270,
                "period": 220, "comma": 220}
    for letter in capital_forms:
        name = f"u{letter.code:05X}"
        shapes[name], advances[name] = fitted(letter, sidebearings)
    for lower in lower_forms:
        name = f"u{lower.code:05X}.lc"
        shapes[name], advances[name] = fitted(lower, sidebearings)
    carets = em_i_ligatures(shapes, advances, capital_forms, lower_forms, sidebearings)
    glyphs = {name: to_glyph(shape) for name, shape in shapes.items()}
    glyphs["space"] = TTGlyphPen(None).glyph()
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics({
        name: (advances[name], round(shapes[name].bounds[0]) if name in shapes else 0)
        for name in names
    })
    fb.setupHorizontalHeader(ascent=850, descent=-200)
    family_base, ps_base = ("New Orkhon Sans", "NewOrkhonSans") if style == "sans" \
        else ("New Orkhon Text", "NewOrkhonText")
    family = family_base + (" Lowercase" if lowercase_default else "")
    ps_name = ps_base + ("Lowercase" if lowercase_default else "") + "-Regular"
    fb.setupNameTable({
        "familyName": family,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{family} {VERSION}",
        "fullName": f"{family} Regular",
        "psName": ps_name,
        "version": f"Version {FONT_VERSION}",
        "copyright": "New Orkhon contributors. Experimental design, 2026.",
        "description": f"A speculative two-case Orkhon {style}. Original paths, not a historical reconstruction.",
        "licenseDescription": (ROOT / "OFL.txt").read_text(),
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(sTypoAscender=850, sTypoDescender=-220, sTypoLineGap=100,
                usWinAscent=850, usWinDescent=220, sxHeight=510, sCapHeight=700)
    fb.setupPost()
    fb.setupMaxp()
    fb.font.recalcTimestamp = False
    fb.font["head"].fontRevision = float(FONT_VERSION)
    fb.font["head"].created = fb.font["head"].modified = 3850070400  # Fixed 2026 epoch.
    if lowercase_default:
        replacements = " ".join(f"sub u{g.code:05X}.lc by u{g.code:05X};" for g in lower_forms)
        replacements += f" sub {EM_I_LIGATURES[1]} by {EM_I_LIGATURES[0]};"
        feature = f"feature ss02 {{ {replacements} }} ss02;"
    else:
        replacements = " ".join(f"sub u{g.code:05X} by u{g.code:05X}.lc;" for g in lower_forms)
        replacements += f" sub {EM_I_LIGATURES[0]} by {EM_I_LIGATURES[1]};"
        feature = f"feature ss01 {{ {replacements} }} ss01;"
    # RTL: shorten the visual-left glyph's advance, not the right-hand AL's advance.
    kern = " ".join(
        f"pos u10C1E.lc <0 0 0 0> {name} <0 0 -{amount} 0>;"
        for name, amount in al_kerning(shapes, advances, capital_forms, lower_forms, sidebearings).items()
    )
    addOpenTypeFeaturesFromString(
        fb.font, f"languagesystem DFLT dflt; languagesystem orkh dflt; "
        f"{feature} feature liga {{ "
        f"sub u10C22 u10C03 by {EM_I_LIGATURES[0]}; "
        f"sub u10C22.lc u10C03.lc by {EM_I_LIGATURES[1]}; "
        f"}} liga; feature kern {{ {kern} }} kern; "
        f"table GDEF {{ {' '.join(f'LigatureCaretByPos {name} {caret};' for name, caret in carets.items())} }} GDEF;"
    )
    output = ROOT / f"{ps_name}.ttf"
    fb.save(output)
    return output, advances


def build():
    output, advances = build_font(False)
    lower_output, lower_advances = build_font(True)
    sans_output, sans_advances = build_font(False, "sans")
    sans_lower_output, sans_lower_advances = build_font(True, "sans")
    lines = ["code\tname\tprinciples\tleft_class\tright_class\tadvance\tdecision"]
    for letter in LETTERS:
        name = f"u{letter.code:05X}"
        lines.append(
            f"U+{letter.code:05X}\t{unicodedata.name(chr(letter.code)).split('ORKHON ')[1]}"
            f"\t{letter.rule}\t{letter.sides[0]}\t{letter.sides[1]}"
            f"\t{advances[name]}\t{letter.decision}"
        )
    (ROOT / "glyph-decisions.tsv").write_text("\n".join(lines) + "\n")
    lower_lines = ["code\tname\ttop\tbottom\tleft_class\tright_class\tadvance\tdecision"]
    for lower in LOWER:
        name = f"u{lower.code:05X}.lc"
        lower_lines.append(
            f"U+{lower.code:05X}\t{unicodedata.name(chr(lower.code)).split('ORKHON ')[1]}"
            f"\t{lower.top}\t{lower.bottom}\t{lower.sides[0]}\t{lower.sides[1]}"
            f"\t{lower_advances[name]}\t{lower.decision}"
        )
    (ROOT / "lowercase-decisions.tsv").write_text("\n".join(lower_lines) + "\n")
    sans_lines = ["code\tname\tcapital_advance\tlowercase_advance"]
    for letter in LETTERS:
        sans_lines.append(
            f"U+{letter.code:05X}\t{unicodedata.name(chr(letter.code)).split('ORKHON ')[1]}"
            f"\t{sans_advances[f'u{letter.code:05X}']}"
            f"\t{sans_lower_advances[f'u{letter.code:05X}.lc']}"
        )
    (ROOT / "sans-decisions.tsv").write_text("\n".join(sans_lines) + "\n")
    print(f"{output} {lower_output} {sans_output} {sans_lower_output}: "
          f"{len(LETTERS)} capitals / {len(LOWER)} lowercase, version {VERSION}")


if __name__ == "__main__":
    build()
