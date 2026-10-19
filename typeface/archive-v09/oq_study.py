"""Sideways OQ candidates, kept separate from the release font."""

from dataclasses import replace
from unittest.mock import patch

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

import build
from build import fitted
from feedback import guides
from lowercase import LOWER
from specimen import GRAY, INK, ROOT, RULE, glyph, label
from validate import raster_checks


def candidate(direction):
    original = next(letter for letter in LOWER if letter.code == 0x10C38)
    scale = 510 / 370
    transform = ((0, scale, -.7, 0, 0, -70 * scale) if direction == "left"
                 else (0, -scale, .7, 0, 0, 440 * scale))
    paths = []
    for path in original.paths:
        pen = SVGPathPen(None)
        parse_path(path, TransformPen(pen, transform))
        paths.append(pen.getCommands())
    return replace(
        original, paths=paths, serifs=[], bottom=0,
        sides=("open", "round") if direction == "left" else ("round", "open"),
        decision=f"Experimental sideways OQ with the pole pointing {direction}.",
    )


def candidate_font(direction):
    study = candidate(direction)
    folder = ROOT / "studies" / f"oq-{direction}"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "OFL.txt").write_bytes((ROOT / "OFL.txt").read_bytes())
    letters = [study if letter.code == study.code else letter for letter in LOWER]
    with patch.object(build, "ROOT", folder), patch.object(build, "LOWER", letters):
        path, _ = build.build_font(True)
    font = TTFont(path)
    family = f"New Orkhon OQ {direction.title()} Study"
    for name_id, text in ((1, family), (4, family + " Regular"),
                          (6, f"NewOrkhonOQ{direction.title()}Study-Regular"),
                          (3, family + " experimental 0.9")):
        font["name"].setName(text, name_id, 3, 1, 0x409)
        font["name"].setName(text, name_id, 1, 0, 0)
    font.save(path)
    raster_checks(path, {letter.code for letter in LOWER})
    shape, advance = fitted(study)
    assert shape.is_valid and not shape.interiors
    assert shape.bounds[1] == 0 and shape.bounds[3] == 510
    print(direction, "bounds", shape.bounds, "advance", advance,
          "centroid", round(shape.centroid.y, 2))
    return path


def main():
    paths = [
        ROOT / "NewOrkhonTextLowercase-Regular.ttf",
        candidate_font("left"), candidate_font("right"),
    ]
    image = Image.new("RGB", (1680, 1430), "white")
    draw = ImageDraw.Draw(image)
    label(draw, (65, 35), "OQ / U+10C38 — SIDEWAYS STUDIES", 38, bold=True)
    label(draw, (65, 95), "Same em size. Release OQ unchanged. A/B are experimental lowercase forms.", 23, GRAY)
    columns = (130, 670, 1210)
    for x, title, path in zip(columns, ("CURRENT / UPRIGHT", "A / POLE LEFT", "B / POLE RIGHT"),
                             paths, strict=True):
        label(draw, (x, 175), title, 23, bold=True)
        guides(draw, x, 470, 360)
        glyph(draw, x + 40, 470, chr(0x10C38), path, 360)
    label(draw, (65, 600), "Skeleton rotated ±90°. Width adjusted; body refitted to 0–510. Strokes redrawn at 82/59.", 23)
    label(draw, (65, 640), "No sideways serif slabs. Horizontal pole now uses the family’s thin stroke.", 22, GRAY)
    draw.line((65, 695, 1615, 695), fill=RULE)
    label(draw, (65, 725), "ACTUAL TEXT SIZES / SAME HISTORICAL WORD", 25, bold=True)
    word = "𐰴𐰃𐰞𐰦𐰸𐰑𐰀"
    for y, size in ((805, 24), (865, 32), (940, 48)):
        label(draw, (65, y - 24), f"{size} px", 17, GRAY)
        for x, path in zip(columns, paths, strict=True):
            glyph(draw, x + 280, y, word, path, size, INK, "rs")
    draw.line((65, 985, 1615, 985), fill=RULE)
    label(draw, (65, 1015), "COMPARE A WITH THE EXISTING FAMILY", 25, bold=True)
    for x, code, text, path in (
        (180, 0x10C38, "A / OQ", paths[1]),
        (580, 0x10C23, "AN / no middle pole", paths[0]),
        (980, 0x10C0F, "AEG / pole stays inside", paths[0]),
        (1380, 0x10C20, "AEL / Y", paths[0]),
    ):
        label(draw, (x - 80, 1080), text, 19, GRAY)
        glyph(draw, x, 1240, chr(code), path, 205, INK, "ms")
        draw.line((x - 110, 1240, x + 110, 1240), fill=RULE)
    label(draw, (65, 1325), "Recommendation: A. Its projecting left pole is unlike AEG’s contained bar; B is closer to AEG.", 22)
    label(draw, (65, 1375), "Both pass distinct-raster checks across the 42-letter set at 20/24/32/48 px; readability is untested.", 21, GRAY)
    image.save(ROOT / "oq-sideways-study.png")
    print("Rendered oq-sideways-study.png. No release glyph was modified.")


if __name__ == "__main__":
    main()
