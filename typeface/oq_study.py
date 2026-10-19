"""Sideways OQ candidates, kept separate from the release font."""

from dataclasses import replace
from unittest.mock import patch

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

import build
from build import fitted
from feedback import guides
from lowercase import LOWER, sideways_oq_paths
from specimen import GRAY, INK, ROOT, RULE, glyph, label
from validate import raster_checks


def candidate(direction):
    original = next(letter for letter in LOWER if letter.code == 0x10C38)
    return replace(
        original, paths=sideways_oq_paths(direction), serifs=[], bottom=0,
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
                          (3, family + " experimental 0.9.1")):
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
        ROOT / "archive-v09" / "NewOrkhonTextLowercase-Regular.ttf",
        candidate_font("left"), candidate_font("right"),
    ]
    study_font = TTFont(paths[2])
    release_font = TTFont(ROOT / "NewOrkhonTextLowercase-Regular.ttf")
    glyph_name = "u10C38.lc"
    assert study_font["glyf"][glyph_name].compile(study_font["glyf"]) == \
        release_font["glyf"][glyph_name].compile(release_font["glyf"])
    assert study_font["hmtx"][glyph_name] == release_font["hmtx"][glyph_name]
    image = Image.new("RGB", (1680, 1430), "white")
    draw = ImageDraw.Draw(image)
    label(draw, (65, 35), "OQ / U+10C38 — SIDEWAYS STUDIES", 38, bold=True)
    label(draw, (65, 95), "Same em size. Pole-right B is now the release lowercase form; capital OQ is unchanged.", 23, GRAY)
    columns = (130, 670, 1210)
    for x, title, path in zip(columns, ("BEFORE / 0.9", "A / POLE LEFT", "B / RELEASE 0.9.1"),
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
    label(draw, (65, 1015), "COMPARE RELEASE B WITH THE EXISTING FAMILY", 25, bold=True)
    for x, code, text, path in (
        (180, 0x10C38, "B / OQ", paths[2]),
        (580, 0x10C23, "AN / no middle pole", paths[0]),
        (980, 0x10C0F, "AEG / pole stays inside", paths[0]),
        (1380, 0x10C20, "AEL / Y", paths[0]),
    ):
        label(draw, (x - 80, 1080), text, 19, GRAY)
        glyph(draw, x, 1240, chr(code), path, 205, INK, "ms")
        draw.line((x - 110, 1240, x + 110, 1240), fill=RULE)
    label(draw, (65, 1325), "Selected by the user: B / pole right. Its protruding pole distinguishes it from AEG’s contained bar.", 22)
    label(draw, (65, 1375), "Both pass 42-sign distinct-raster checks at 20/24/32/48 px; reader performance is untested.", 21, GRAY)
    image.save(ROOT / "oq-sideways-study.png")
    print("Rendered oq-sideways-study.png. B is the release lowercase OQ.")


if __name__ == "__main__":
    main()
