"""New Orkhon 0.8: speculative uppercase and lowercase serif forms."""

import math
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from ductus import em_print_path
from lowercase import LOWER

ROOT = Path(__file__).resolve().parent
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
        f"M 380 0 L 380 {ARM_TOP} L 100 {ARM_TOP} L 100 {ARM_TOP - 72}",
        "M 380 350 L 100 350",
    ], [(380, 0, 1)], ("open", "stem"),
        "Two left arms use the single-return family's common cap arm and middle bar."),
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
        "M 110 700 C 340 700 405 530 300 425 C 265 385 185 365 110 350",
        "M 110 350 C 385 340 410 160 300 65 C 245 15 180 0 110 0",
    ], [(110, 0, 1), (110, 700, -1)], ("stem", "round"),
        "One common upright carries two open-looking curved turns, an authored B-like construction unlike ENY's 3."),
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
        "A Latinized mirrored Arabic 3 with a straight right-hand pole beneath its three linked tips."),
    Letter(0x10C32, [
        "M 55 700 C 170 700 215 600 255 500 L 465 0",
        "M 255 500 L 60 0",
    ], [(60, 0, 1), (465, 0, 1)], ("diagonal", "lambda"),
        "A lambda-like rising left leg meets a curved head; its projecting right foot gets a tighter optical side space."),
    Letter(0x10C34, [
        "M 380 0 L 380 700",
        "M 380 330 C 245 350 175 470 105 460 C 175 285 155 125 95 0",
    ], [(380, 0, 1), (380, 700, -1)], ("open", "stem"),
        "A low curling free leg distinguishes q from the upturned r; counter widths are related."),
    Letter(0x10C36, [
        "M 365 685 C 245 675 130 490 85 350 C 130 210 245 25 365 15 L 365 685",
    ], [(365, 0, 1), (365, 700, -1)], ("diagonal", "stem"),
        "The rounded triangle shares full height with the round bowl but preserves its pointed side."),
    Letter(0x10C38, [
        "M 265 700 L 265 0",
        "M 75 285 C 170 285 235 165 265 0 C 295 165 360 285 455 285",
    ], [(265, 700, -1)], ("open", "open"),
        "Two low wings meet at the baseline without the old offset-generated central burr."),
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
        *Y_STROKES, "M 105 200 L 435 200",
    ], Y_SERIFS, ("diagonal", "diagonal"),
        "Correct the inherited extra prong: the reference has a two-pronged fork and low crossbar, so use Y plus bar."),
    Letter(0x10C43, [
        "M 85 500 L 270 700 L 455 500",
        "M 270 700 L 270 355",
        "M 270 355 C 180 325 115 235 105 175 C 140 80 205 0 270 0 C 335 0 400 80 435 175 C 425 235 360 325 270 355",
    ], [], ("diagonal", "diagonal"),
        "A suspended eye and a roof share a clean junction; the pole stops at the apex.",
        round_bottom=True),
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
        "M 115 0 L 115 700 C 255 615 345 85 485 0 L 485 700 C 345 615 255 85 115 0",
    ], [(115, 0, 1), (485, 0, 1), (115, 700, -1), (485, 700, -1)],
        ("stem", "stem"), "Equal posts and woven curves preserve two counters without extra jagged endpoints."),
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


def stroke(path, stem=STEM, hair=HAIRLINE):
    line = LineString(points(path))
    normalized = affinity.scale(line, 2 / stem, 2 / hair, origin=(0, 0))
    closed = line.is_closed
    shape = normalized.buffer(1, cap_style="round" if closed else "flat",
                              join_style="round", quad_segs=12)
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


def geometry(letter):
    stem = getattr(letter, "stroke_stem", STEM)
    hair = getattr(letter, "stroke_hair", HAIRLINE)
    base = getattr(letter, "bottom", 0)
    cap = getattr(letter, "top", HEIGHT)
    shape = unary_union([
        *(stroke(p, stem, hair) for p in letter.paths),
        *(foot(x, y, direction, stem) for x, y, direction in letter.serifs),
        *(Point(x, y).buffer(r, quad_segs=24) for x, y, r in letter.dots),
    ]).simplify(.3, preserve_topology=True)
    assert shape.is_valid, f"Invalid outline U+{letter.code:05X}"
    bottom = base - OVERSHOOT if letter.round_bottom else base
    top = cap + OVERSHOOT if letter.round_top else cap
    # Baseline/cap serifs must meet a flat edge, even on an inclined stroke.
    clip_bottom = base if any(y == base for _, y, _ in letter.serifs) else -2000
    clip_top = cap if any(y == cap for _, y, _ in letter.serifs) else 2000
    shape = shape.intersection(box(-2000, clip_bottom, 2000, clip_top))
    _, y0, _, y1 = shape.bounds
    shape = affinity.translate(shape, yoff=-y0)
    shape = affinity.scale(shape, yfact=(top - bottom) / (y1 - y0), origin=(0, 0))
    return affinity.translate(shape, yoff=bottom)


def fitted(letter):
    shape = geometry(letter)
    x0, _, x1, _ = shape.bounds
    left, right = (SIDES[side] for side in letter.sides)
    shape = affinity.translate(shape, xoff=left - x0)
    return shape, round(x1 - x0 + left + right)


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


def build_font(lowercase_default):
    names = [".notdef", "space", "divider", "period", "comma"]
    names += [f"u{g.code:05X}" for g in LETTERS]
    names += [f"u{g.code:05X}.lc" for g in LOWER]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(names)
    cmap = {32: "space", 0x205A: "divider", 46: "period", 44: "comma"}
    cmap.update({
        g.code: f"u{g.code:05X}{'.lc' if lowercase_default else ''}"
        for g in LETTERS
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
    for letter in LETTERS:
        name = f"u{letter.code:05X}"
        shapes[name], advances[name] = fitted(letter)
    for lower in LOWER:
        name = f"u{lower.code:05X}.lc"
        shapes[name], advances[name] = fitted(lower)
    glyphs = {name: to_glyph(shape) for name, shape in shapes.items()}
    glyphs["space"] = TTGlyphPen(None).glyph()
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics({
        name: (advances[name], round(shapes[name].bounds[0]) if name in shapes else 0)
        for name in names
    })
    fb.setupHorizontalHeader(ascent=850, descent=-200)
    family = "New Orkhon Text Lowercase" if lowercase_default else "New Orkhon Text"
    ps_name = "NewOrkhonTextLowercase-Regular" if lowercase_default else "NewOrkhonText-Regular"
    fb.setupNameTable({
        "familyName": family,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{family} 0.8",
        "fullName": f"{family} Regular",
        "psName": ps_name,
        "version": "Version 0.800",
        "copyright": "New Orkhon contributors. Experimental design, 2026.",
        "description": "A speculative two-case Orkhon serif. Original paths, not a historical reconstruction.",
        "licenseDescription": (ROOT / "OFL.txt").read_text(),
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(sTypoAscender=850, sTypoDescender=-220, sTypoLineGap=100,
                usWinAscent=850, usWinDescent=220, sxHeight=510, sCapHeight=700)
    fb.setupPost()
    fb.setupMaxp()
    if lowercase_default:
        replacements = " ".join(f"sub u{g.code:05X}.lc by u{g.code:05X};" for g in LOWER)
        feature = f"feature ss02 {{ {replacements} }} ss02;"
    else:
        replacements = " ".join(f"sub u{g.code:05X} by u{g.code:05X}.lc;" for g in LOWER)
        feature = f"feature ss01 {{ {replacements} }} ss01;"
    addOpenTypeFeaturesFromString(fb.font, feature)
    output = ROOT / f"{ps_name}.ttf"
    fb.save(output)
    return output, advances


def build():
    output, advances = build_font(False)
    lower_output, lower_advances = build_font(True)
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
    print(f"{output} and {lower_output}: {len(LETTERS)} uppercase / {len(LOWER)} lowercase, version 0.8")


if __name__ == "__main__":
    build()
