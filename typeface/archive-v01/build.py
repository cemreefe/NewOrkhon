"""Hand-drawn New Orkhon study; build with fonttools, shapely, pillow."""

import math
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent


@dataclass
class Letter:
    code: int
    width: int
    paths: list[str]
    serifs: list[tuple[int, int, int]]
    rule: str
    decision: str
    dots: tuple = ()


LETTERS = [
    Letter(0x10C00, 450, [
        "M 225 700 L 225 40 C 225 -10 120 -10 95 70",
        "M 225 700 C 295 680 315 630 355 625",
    ], [], "1,2,3", "Two opposed ends survive; the lower elbow becomes a returning pen stroke."),
    Letter(0x10C03, 420, [
        "M 145 0 L 145 700 C 245 700 260 620 335 615",
    ], [(145, 0, 1)], "1,2,3", "The single raised flag becomes a shoulder on an ascender; no lower return."),
    Letter(0x10C06, 430, [
        "M 155 700 C 150 580 180 530 300 470",
        "M 300 470 C 125 420 105 230 145 -12",
    ], [], "1,3,5", "Keep the middle rightward cusp, but make the two turns unequal and flowing."),
    Letter(0x10C07, 540, [
        "M 140 0 L 140 510 C 250 520 270 320 395 320 L 395 700",
    ], [(140, 0, 1), (395, 700, -1)], "1,2,3", "Replace the rigid N diagonal with a descending shoulder; retain two opposed posts."),
    Letter(0x10C09, 500, [
        "M 220 700 C 100 620 190 560 290 485 C 490 300 370 -12 235 -12 C 55 -12 55 260 120 350",
    ], [], "1,2,3", "The open bowl becomes a low counter and tall returned neck, not a Latin b."),
    Letter(0x10C0B, 500, [
        "M 250 714 C 130 660 95 540 250 440 C 405 530 375 650 250 714",
        "M 250 440 L 100 0", "M 250 440 L 395 0",
    ], [(100, 0, 1), (395, 0, 1)], "1,4,5", "Diamond becomes a pear-shaped eye; crossed legs remain diagnostic."),
    Letter(0x10C0D, 650, [
        "M 110 690 C 310 610 310 490 110 430",
        "M 540 690 C 340 610 340 490 540 430",
        "M 325 320 L 325 -140",
    ], [(325, -140, 1)], "1,2,5", "Opposed upper bows and a detached low stem keep the three-part identity."),
    Letter(0x10C0F, 490, [
        "M 370 660 C 90 810 40 170 335 -12",
        "M 140 450 C 220 450 270 375 345 360",
    ], [], "1,3,5", "The open bow and internal bar stay open; neither is replaced by a closed e."),
    Letter(0x10C11, 650, [
        "M 110 700 C 300 630 300 555 110 485 C 300 415 300 340 110 270 C 300 190 300 115 110 0",
        "M 395 700 C 585 630 585 555 395 485 C 585 415 585 340 395 270 C 585 190 585 115 395 0",
    ], [], "1,3,5", "Twin zigzags become paired serpentine strokes; do not merge their channels."),
    Letter(0x10C13, 540, [
        "M 110 700 C 200 490 345 185 430 0",
        "M 430 700 C 335 490 200 185 110 0",
    ], [(110, 0, 1), (430, 0, 1)], "1,4,5", "Keep the cross, but bow the diagonals and lighten one stroke optically."),
    Letter(0x10C14, 620, [
        "M 300 -140 L 300 700", "M 110 -140 L 110 270 L 510 270 L 510 700",
    ], [(300, 700, -1), (110, -140, 1), (300, -140, 1), (510, 700, -1)],
        "2,4,5", "Crossed rails move to body height; staggered verticals retain the asymmetry."),
    Letter(0x10C16, 510, [
        "M 125 0 L 125 520 C 510 510 510 0 125 0",
    ], [(125, 0, 1)], "1,2,3", "The triangular D-like enclosure becomes one low bowl with an upright spine."),
    Letter(0x10C18, 500, [
        "M 125 350 C 0 770 520 790 400 450 C 370 350 235 320 235 190 L 235 0",
    ], [(235, 0, 1)], "1,2,5", "Retain the open head and down-going hook; redistribute height into the neck."),
    Letter(0x10C1A, 480, [
        "M 345 0 L 345 700 C 260 700 235 620 130 615",
        "M 345 360 C 250 360 220 455 130 465",
    ], [(345, 0, 1)], "1,4,5", "Two left-facing flags become shoulders; distinct from the single-flag p."),
    Letter(0x10C1C, 490, [
        "M 125 0 L 125 700 C 245 700 300 660 360 610",
        "M 125 350 C 240 390 355 380 355 265 L 355 0",
    ], [(125, 0, 1), (355, 0, 1)], "1,2,4", "The top square opens into a flag, the lower square into a low shoulder."),
    Letter(0x10C1E, 400, [
        "M 270 700 L 270 0 C 190 0 125 75 90 95",
    ], [(270, 700, -1)], "1,2,4", "A tall stem with a lower left return; it must not acquire the vowel's top flag."),
    Letter(0x10C20, 490, [
        "M 245 0 L 245 370 C 190 460 125 520 95 560",
        "M 245 370 C 300 460 365 520 395 560",
    ], [(245, 0, 1)], "1,2,4", "The fork moves to body height; its upright is a lower stem, not an ascender."),
    Letter(0x10C21, 610, [
        "M 120 0 L 120 700 C 220 690 240 510 305 500 C 370 510 390 690 490 700 L 490 0",
    ], [(120, 0, 1), (490, 0, 1)], "1,3,4", "A rigid M becomes two tall uprights around a flowing central valley."),
    Letter(0x10C22, 620, [
        "M 100 550 L 480 250 L 245 -12",
        "M 245 714 L 535 460 L 100 100",
    ], [], "1,3,5", "Retain the woven diamond and projecting ends; soften direction changes only."),
    Letter(0x10C23, 400, [
        "M 110 520 C 400 450 400 60 110 -12",
    ], [], "1,2,5", "One bow becomes a low asymmetric curve; no cusp or added return."),
    Letter(0x10C24, 600, [
        "M 135 700 L 135 275 C 220 260 265 175 330 150 L 330 -140",
        "M 330 150 L 330 450 C 420 440 450 355 480 340 L 480 700",
    ], [(135, 700, -1), (330, -140, 1), (480, 700, -1)],
        "1,2,4", "The doubled staggered joints become shoulders around a shared descending stem."),
    Letter(0x10C26, 600, [
        "M 110 520 C -10 -200 610 -200 490 520",
    ], [], "1,2,5", "A low bowl holds three separate dots; simplify neither their number nor spacing.",
        ((235, 350, 27), (365, 350, 27), (300, 200, 27))),
    Letter(0x10C28, 450, [
        "M 130 700 C 110 560 280 575 295 455 L 180 390 C 290 350 285 285 180 245 C 90 205 100 100 115 0",
    ], [], "1,2,5", "Keep two right-pointing turns; vary their size rather than reducing to the vowel cusp."),
    Letter(0x10C2A, 450, [
        "M 115 520 C 430 460 430 60 115 -12",
        "M 220 350 L 280 275 L 200 220",
    ], [], "1,4,5", "Use the n-bow family with its inner kink retained as the distinguishing notch."),
    Letter(0x10C2D, 420, [
        "M 285 700 L 285 0", "M 285 330 C 210 335 160 430 100 450",
    ], [(285, 0, 1), (285, 700, -1)], "1,2,4", "Central left branch stays on a full-height stem, unlike the bottom-return l."),
    Letter(0x10C2F, 420, [
        "M 285 0 L 285 700 C 200 690 165 600 95 575",
    ], [(285, 0, 1)], "1,2,4", "Single left shoulder on a tall stem; share the k-family shoulder without its second bar."),
    Letter(0x10C30, 520, [
        "M 130 700 L 130 0",
        "M 130 580 C 240 620 335 700 390 700 L 390 490",
        "M 130 260 C 240 285 325 350 390 350 L 390 0",
    ], [(130, 0, 1), (390, 0, 1), (130, 700, -1)], "1,2,4",
        "Two rightward tiers retain their short end stems; align the lower tier to the text zone."),
    Letter(0x10C31, 490, [
        "M 245 -140 L 245 450",
        "M 245 450 C 190 540 125 650 95 700",
        "M 245 450 C 300 540 365 650 395 700",
    ], [(245, -140, 1)], "2,4,5", "Tall fork plus descender stays distinct from the low fork l."),
    Letter(0x10C32, 490, [
        "M 245 700 L 245 180",
        "M 245 180 C 190 100 125 25 95 -12",
        "M 245 180 C 300 100 365 25 395 -12",
    ], [(245, 700, -1)], "1,2,4", "Inverted fork keeps two feet; do not round it into the u-shaped q sign."),
    Letter(0x10C34, 530, [
        "M 375 0 L 375 700", "M 375 250 C 240 300 170 390 110 380 C 170 240 150 90 95 -12",
    ], [(375, 0, 1), (375, 700, -1)], "1,2,5", "A low left branch and curling free leg retain the q sign's asymmetric join."),
    Letter(0x10C36, 490, [
        "M 355 520 C 255 510 145 370 100 260 C 145 150 255 10 355 0 L 355 520",
    ], [(355, 0, 1)], "1,2,5", "Pointed triangle becomes a low teardrop; its left point distinguishes it from y's round bowl."),
    Letter(0x10C38, 520, [
        "M 260 700 L 260 0",
        "M 80 220 C 160 220 235 140 260 0 C 285 140 360 220 440 220",
    ], [(260, 700, -1)], "1,2,5", "Two low curved wings meet a tall stem; preserve the low central meeting point."),
    Letter(0x10C3A, 530, [
        "M 375 0 L 375 700",
        "M 375 300 C 275 300 205 190 105 150 C 185 285 175 420 105 510",
    ], [(375, 0, 1), (375, 700, -1)], "1,4,5", "Reverse the q-family free-leg turn upward; do not normalize away that distinction."),
    Letter(0x10C3C, 540, [
        "M 270 0 L 270 520",
        "M 85 430 C 140 465 150 520 180 520 C 215 520 240 465 270 440 C 300 465 325 520 360 520 C 390 520 400 465 455 430",
    ], [(270, 0, 1)], "1,2,4", "Twin roof peaks become two shoulders; preserve both, not a plain Y."),
    Letter(0x10C3D, 500, [
        "M 175 700 C 20 570 100 430 245 390 C 390 350 365 160 310 -12",
        "M 245 390 C 245 570 315 660 400 650",
    ], [], "1,2,5", "The branching curve gets a low spine and a high right shoulder; retain the branch."),
    Letter(0x10C3E, 300, [
        "M 150 0 L 150 520",
    ], [(150, 0, 1), (150, 520, -1)], "2,4,5",
        "A simple minim; do not add a dot, which would invent another identifying mark."),
    Letter(0x10C3F, 530, [
        "M 265 530 C 45 530 45 -12 265 -12 C 485 -12 485 530 265 530",
    ], [], "1,2,5", "Square syllabic sign becomes a low oval counter, with optical overshoot."),
    Letter(0x10C41, 500, [
        "M 250 -140 L 250 450",
        "M 250 450 C 190 540 130 650 100 700",
        "M 250 450 C 310 540 370 650 400 700",
        "M 95 150 L 405 150",
    ], [(250, -140, 1)], "2,4,5", "Crossed tall fork keeps its crossbar below the split; never merge with the plain fork."),
    Letter(0x10C43, 540, [
        "M 100 500 L 270 700 L 440 500",
        "M 270 700 L 270 350",
        "M 270 350 C 200 320 135 235 115 175 C 150 110 210 20 270 -12 C 330 20 390 110 425 175 C 405 235 340 320 270 350",
    ], [], "1,2,5", "Retain roof over a suspended eye; lower the eye rather than make a second aeb."),
    Letter(0x10C45, 550, [
        "M 135 0 L 135 700",
        "M 135 280 C 230 285 325 420 400 420 C 340 310 350 90 440 -12",
    ], [(135, 0, 1), (135, 700, -1)], "1,2,4", "Keep the left ascender and low right falling leg; a low shoulder replaces the high diagonal."),
    Letter(0x10C47, 570, [
        "M 120 -12 C -40 570 610 570 450 -12",
        "M 285 505 L 285 700", "M 285 505 C 350 580 395 660 430 690",
    ], [(285, 700, -1)], "1,2,5", "Keep the lower opening and top branch; this is not the closed oval ash sign."),
    Letter(0x10C48, 620, [
        "M 120 0 L 120 700 C 250 640 370 150 500 0 L 500 700 C 370 640 250 150 120 0",
    ], [(120, 0, 1), (500, 0, 1)], "1,3,5",
        "Two posts and crossed diagonals become woven curves; retain two separate counters."),
]


def points(path):
    pen = RecordingPen()
    parse_path(path, pen)
    result = []
    current = None
    for op, values in pen.value:
        if op == "moveTo":
            current = values[0]
            result.append(current)
        elif op == "lineTo":
            target = values[0]
            n = max(2, int(math.dist(current, target) / 8))
            result += [(current[0] + (target[0] - current[0]) * i / n,
                        current[1] + (target[1] - current[1]) * i / n)
                       for i in range(1, n + 1)]
            current = target
        elif op == "curveTo":
            a, b, c = values
            n = max(12, int((math.dist(current, a) + math.dist(a, b)
                             + math.dist(b, c)) / 8))
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
    pts = points(path)
    left, right = [], []
    closed = math.dist(pts[0], pts[-1]) < 1
    for i, (x, y) in enumerate(pts):
        prev = pts[i - 1] if i else (pts[-2] if closed else pts[0])
        nxt = pts[i + 1] if i < len(pts) - 1 else (pts[1] if closed else pts[-1])
        dx, dy = nxt[0] - prev[0], nxt[1] - prev[1]
        length = math.hypot(dx, dy)
        nx, ny = -dy / length, dx / length
        angle = math.radians(15)
        u = nx * math.cos(angle) + ny * math.sin(angle)
        v = -nx * math.sin(angle) + ny * math.cos(angle)
        half = math.hypot(32 * u, 13 * v)
        left.append((x + nx * half, y + ny * half))
        right.append((x - nx * half, y - ny * half))
    poly = Polygon(left + right[::-1])
    return poly.buffer(0)


def foot(x, y, direction):
    return Polygon([
        (x - 58, y), (x + 58, y),
        (x + 58, y + direction * 15),
        (x + 42, y + direction * 19),
        (x + 33, y + direction * 35),
        (x + 31, y + direction * 49),
        (x - 31, y + direction * 49),
        (x - 33, y + direction * 35),
        (x - 42, y + direction * 19),
        (x - 58, y + direction * 15),
    ])


def geometry(letter):
    return unary_union([
        *(stroke(p) for p in letter.paths),
        *(foot(*f) for f in letter.serifs),
        *(Point(x, y).buffer(r, quad_segs=16) for x, y, r in letter.dots),
    ]).buffer(0)


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
        "divider": unary_union([Point(135, y).buffer(28) for y in (180, 390)]),
        "period": Point(110, 30).buffer(30),
        "comma": stroke("M 125 70 C 170 -10 130 -70 85 -90"),
    }
    shapes.update({f"u{g.code:05X}": geometry(g) for g in LETTERS})
    glyphs = {n: to_glyph(s) for n, s in shapes.items()}
    glyphs["space"] = TTGlyphPen(None).glyph()
    fb.setupGlyf(glyphs)
    advances = {".notdef": 560, "space": 260, "divider": 270,
                "period": 220, "comma": 220}
    advances.update({f"u{g.code:05X}": g.width for g in LETTERS})
    fb.setupHorizontalMetrics({
        n: (advances[n], round(shapes[n].bounds[0]) if n in shapes else 0)
        for n in names
    })
    fb.setupHorizontalHeader(ascent=850, descent=-250)
    fb.setupNameTable({
        "familyName": "New Orkhon Text",
        "styleName": "Regular",
        "uniqueFontIdentifier": "New Orkhon Text 0.1",
        "fullName": "New Orkhon Text Regular",
        "psName": "NewOrkhonText-Regular",
        "version": "Version 0.100",
        "copyright": "New Orkhon contributors. Experimental design, 2026.",
        "description": "A speculative unicasal Orkhon text hand. Hand-authored outlines, not a historical reconstruction.",
        "licenseDescription": "Licensed under the SIL Open Font License, Version 1.1.",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(sTypoAscender=850, sTypoDescender=-250, sTypoLineGap=120,
                usWinAscent=850, usWinDescent=250, sxHeight=520, sCapHeight=700)
    fb.setupPost()
    fb.setupMaxp()
    output = ROOT / "NewOrkhonText-Regular.ttf"
    fb.save(output)
    (ROOT / "glyph-decisions.tsv").write_text(
        "code\tname\tprinciples\tdecision\n" + "\n".join(
            f"U+{g.code:05X}\t{unicodedata.name(chr(g.code)).split('ORKHON ')[1]}"
            f"\t{g.rule},6\t{g.decision}" for g in LETTERS
        ) + "\n"
    )
    print(f"{output}: {len(LETTERS)} hand-authored Orkhon glyphs")


if __name__ == "__main__":
    build()
