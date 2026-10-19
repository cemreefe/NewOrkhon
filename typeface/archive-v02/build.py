"""New Orkhon 0.2: a unicasal serif with fitted, not fixed-width, spacing."""

import math
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent
HEIGHT, OVERSHOOT = 700, 10
STEM, HAIRLINE = 64, 30
SIDES = {"stem": 55, "round": 32, "diagonal": 26, "open": 18}


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
        "M 225 685 L 225 95 C 225 15 135 15 95 75",
        "M 225 685 C 280 685 300 625 355 610",
    ], [], ("round", "open"), "Opposed end returns share the same cap and baseline as the single flag."),
    Letter(0x10C03, [
        "M 145 0 L 145 685 C 235 685 260 610 330 610",
    ], [(145, 0, 1)], ("stem", "open"), "Flag, stem and foot use the common weight and height."),
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
        "The opposed horns and detached stem remain separate but occupy the shared height."),
    Letter(0x10C0F, [
        "M 390 675 C 60 850 45 115 370 0",
        "M 110 385 C 220 385 265 290 355 280",
    ], [], ("round", "open"), "An open bow, a clean internal bar, and room for the open counter.",
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
        "M 300 0 L 300 700", "M 110 0 L 110 350 L 490 350 L 490 700",
    ], [(300, 700, -1), (110, 0, 1), (300, 0, 1), (490, 700, -1)], ("stem", "stem"),
        "Staggered rails now share one baseline and cap line; the bar sits on the common middle."),
    Letter(0x10C16, [
        "M 120 15 L 120 685 C 560 685 560 15 120 15",
    ], [(120, 0, 1), (120, 700, -1)], ("stem", "round"),
        "The bowl shares the oval's counter width and the common full-height text body."),
    Letter(0x10C18, [
        "M 120 395 C -15 820 525 820 405 425 C 370 305 250 285 250 130 L 250 0",
    ], [(250, 0, 1)], ("round", "round"),
        "An open head and descending hook with one clean, continuous outline.", round_top=True),
    Letter(0x10C1A, [
        "M 350 0 L 350 685 C 255 685 230 605 125 605",
        "M 350 320 C 250 320 215 405 125 415",
    ], [(350, 0, 1)], ("open", "stem"),
        "Both left shoulders use the same curve model as the single-shoulder p."),
    Letter(0x10C1C, [
        "M 125 0 L 125 685 C 230 685 295 630 355 590",
        "M 125 350 C 260 390 375 370 375 250 L 375 0",
    ], [(125, 0, 1), (375, 0, 1)], ("stem", "open"),
        "An open upper flag and a lower arch replace the rectangular construction."),
    Letter(0x10C1E, [
        "M 285 700 L 285 15 C 205 15 135 75 90 105",
    ], [(285, 700, -1)], ("open", "stem"),
        "A bottom return instead of the vowel's top flag, at the same overall height."),
    Letter(0x10C20, [
        "M 250 0 L 250 350 C 190 450 125 600 90 700",
        "M 250 350 C 310 450 375 600 410 700",
    ], [(250, 0, 1)], ("diagonal", "diagonal"),
        "The plain fork has two upper prongs; it is not a shrunk version of another sign."),
    Letter(0x10C21, [
        "M 115 0 L 115 685 C 215 685 230 420 300 405 C 370 420 385 685 485 685 L 485 0",
    ], [(115, 0, 1), (485, 0, 1)], ("stem", "stem"),
        "Two equal posts frame a smooth valley; both feet and shoulders follow the shared system."),
    Letter(0x10C22, [
        "M 95 545 L 465 250 L 235 0",
        "M 235 700 L 530 450 L 95 110",
    ], [], ("diagonal", "diagonal"),
        "The woven centre stays open; joined strokes no longer form offset spikes."),
    Letter(0x10C23, [
        "M 100 700 C 485 600 485 100 100 0",
    ], [], ("open", "round"),
        "The plain bow has the same full-height curvature as the notched bow."),
    Letter(0x10C24, [
        "M 115 700 L 115 350 C 220 350 250 180 320 165 L 320 0",
        "M 320 165 L 320 515 C 410 515 450 350 485 350 L 485 700",
    ], [(115, 700, -1), (320, 0, 1), (485, 700, -1)], ("stem", "stem"),
        "Repeated shoulders share their curvature and internal spacing; no arbitrary descender."),
    Letter(0x10C26, [
        "M 110 700 C -40 -230 640 -230 490 700",
    ], [], ("round", "round"),
        "A full-height open bowl holds three well-separated dots, not a cramped low component.",
        round_bottom=True, dots=((230, 460, 27), (370, 460, 27), (300, 270, 27))),
    Letter(0x10C28, [
        "M 125 700 C 125 570 300 555 300 455 L 175 380 C 295 335 290 245 180 210 C 95 180 105 85 105 0",
    ], [], ("round", "open"),
        "Two unequal turns stay distinct from the single vowel cusp; no self-overlapping stroke edge."),
    Letter(0x10C2A, [
        "M 100 700 C 485 600 485 100 100 0",
        "M 250 465 L 310 350 L 230 270",
    ], [], ("open", "round"),
        "The n bow and ny bow share a counter; ny keeps a clear internal notch."),
    Letter(0x10C2D, [
        "M 285 700 L 285 0", "M 285 350 C 205 350 150 440 95 460",
    ], [(285, 0, 1), (285, 700, -1)], ("open", "stem"),
        "The mid-stem branch stays distinct from a bottom return without using a different cap height."),
    Letter(0x10C2F, [
        "M 285 0 L 285 685 C 195 685 160 605 95 590",
    ], [(285, 0, 1)], ("open", "stem"),
        "A single shoulder uses the k family's stem, shoulder tension and side space."),
    Letter(0x10C30, [
        "M 125 700 L 125 0",
        "M 125 540 C 245 565 310 685 390 685 L 390 500",
        "M 125 230 C 245 255 310 370 390 370 L 390 0",
    ], [(125, 0, 1), (390, 0, 1), (125, 700, -1)], ("stem", "stem"),
        "Two tiers and short end stems share a standard shoulder and an open lower counter."),
    Letter(0x10C31, [
        "M 250 0 L 250 700",
        "M 250 350 C 190 450 125 600 90 700",
        "M 250 350 C 310 450 375 600 410 700",
    ], [(250, 0, 1)], ("diagonal", "diagonal"),
        "Restore the reference sign's middle prong: a trident, not a plain fork with a makeshift descender."),
    Letter(0x10C32, [
        "M 250 700 L 250 350",
        "M 250 350 C 190 250 125 100 90 0",
        "M 250 350 C 310 250 375 100 410 0",
    ], [(250, 700, -1)], ("diagonal", "diagonal"),
        "The inverted fork uses the same branch shape and weight as the upright fork."),
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
        "M 175 700 C 10 540 95 430 250 350 C 400 270 370 125 305 0",
        "M 250 350 C 230 530 315 685 405 685",
    ], [], ("round", "round"),
        "A branched curve with a larger, cleaner central aperture."),
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
        "M 250 0 L 250 700",
        "M 250 350 C 190 450 125 600 90 700",
        "M 250 350 C 310 450 375 600 410 700",
        "M 85 200 L 415 200",
    ], [(250, 0, 1)], ("diagonal", "diagonal"),
        "The crossed trident keeps both its middle prong and its separate low crossbar."),
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
        "M 100 0 C -70 700 640 700 470 0",
        "M 285 500 L 285 700",
        "M 285 500 C 350 570 390 645 435 685",
    ], [(285, 700, -1)], ("round", "round"),
        "The open arch uses the oval family's counter; the upper two-pronged branch remains clear."),
    Letter(0x10C48, [
        "M 115 0 L 115 700 C 255 615 345 85 485 0 L 485 700 C 345 615 255 85 115 0",
    ], [(115, 0, 1), (485, 0, 1), (115, 700, -1), (485, 700, -1)],
        ("stem", "stem"), "Equal posts and woven curves preserve two counters without extra jagged endpoints."),
]


def points(path):
    pen = RecordingPen()
    parse_path(path, pen)
    result, current = [], None
    for op, values in pen.value:
        if op == "moveTo":
            if result:
                raise ValueError("Use a separate path for each contour.")
            current = values[0]
            result.append(current)
        elif op == "lineTo":
            target = values[0]
            n = max(2, math.ceil(math.dist(current, target) / 3))
            result.extend((current[0] + (target[0] - current[0]) * i / n,
                           current[1] + (target[1] - current[1]) * i / n)
                          for i in range(1, n + 1))
            current = target
        elif op == "curveTo":
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


def stroke(path):
    line = LineString(points(path))
    normalized = affinity.scale(line, 2 / STEM, 2 / HAIRLINE, origin=(0, 0))
    closed = line.is_closed
    shape = normalized.buffer(1, cap_style="round" if closed else "flat",
                              join_style="round", quad_segs=12)
    return affinity.scale(shape, STEM / 2, HAIRLINE / 2, origin=(0, 0))


def foot(x, y, direction):
    return Polygon([
        (x - 54, y), (x + 54, y), (x + 54, y + direction * 14),
        (x + 42, y + direction * 18), (x + 34, y + direction * 34),
        (x + 32, y + direction * 48), (x - 32, y + direction * 48),
        (x - 34, y + direction * 34), (x - 42, y + direction * 18),
        (x - 54, y + direction * 14),
    ])


def geometry(letter):
    shape = unary_union([
        *(stroke(p) for p in letter.paths),
        *(foot(*f) for f in letter.serifs),
        *(Point(x, y).buffer(r, quad_segs=24) for x, y, r in letter.dots),
    ]).simplify(.3, preserve_topology=True)
    assert shape.is_valid, f"Invalid outline U+{letter.code:05X}"
    bottom = -OVERSHOOT if letter.round_bottom else 0
    top = HEIGHT + OVERSHOOT if letter.round_top else HEIGHT
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


def build():
    names = [".notdef", "space", "divider", "period", "comma"]
    names += [f"u{g.code:05X}" for g in LETTERS]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(names)
    cmap = {32: "space", 0x205A: "divider", 46: "period", 44: "comma"}
    cmap.update({g.code: f"u{g.code:05X}" for g in LETTERS})
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
    glyphs = {name: to_glyph(shape) for name, shape in shapes.items()}
    glyphs["space"] = TTGlyphPen(None).glyph()
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics({
        name: (advances[name], round(shapes[name].bounds[0]) if name in shapes else 0)
        for name in names
    })
    fb.setupHorizontalHeader(ascent=850, descent=-200)
    fb.setupNameTable({
        "familyName": "New Orkhon Text",
        "styleName": "Regular",
        "uniqueFontIdentifier": "New Orkhon Text 0.2",
        "fullName": "New Orkhon Text Regular",
        "psName": "NewOrkhonText-Regular",
        "version": "Version 0.200",
        "copyright": "New Orkhon contributors. Experimental design, 2026.",
        "description": "A speculative unicasal Orkhon serif. Original paths, not a historical reconstruction.",
        "licenseDescription": (ROOT / "OFL.txt").read_text(),
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(sTypoAscender=850, sTypoDescender=-200, sTypoLineGap=100,
                usWinAscent=850, usWinDescent=200, sxHeight=700, sCapHeight=700)
    fb.setupPost()
    fb.setupMaxp()
    output = ROOT / "NewOrkhonText-Regular.ttf"
    fb.save(output)
    lines = ["code\tname\tprinciples\tleft_class\tright_class\tadvance\tdecision"]
    for letter in LETTERS:
        name = f"u{letter.code:05X}"
        lines.append(
            f"U+{letter.code:05X}\t{unicodedata.name(chr(letter.code)).split('ORKHON ')[1]}"
            f"\t{letter.rule}\t{letter.sides[0]}\t{letter.sides[1]}"
            f"\t{advances[name]}\t{letter.decision}"
        )
    (ROOT / "glyph-decisions.tsv").write_text("\n".join(lines) + "\n")
    print(f"{output}: {len(LETTERS)} fitted Orkhon glyphs, version 0.2")


if __name__ == "__main__":
    build()
