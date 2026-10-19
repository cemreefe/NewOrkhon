"""Measured 0.8/0.9 proofs; no changes to the proposed OQ construction."""

import json
import runpy
import unicodedata

from PIL import Image, ImageDraw

from build import fitted, geometry, stroke
from lowercase import LOWER
from specimen import GRAY, INK, ROOT, RULE, glyph, label

OLD = ROOT / "archive-v08" / "NewOrkhonTextLowercase-Regular.ttf"
NEW = ROOT / "NewOrkhonTextLowercase-Regular.ttf"
CODES = (0x10C3A, 0x10C07, 0x10C1E, 0x10C34, 0x10C23, 0x10C38)


def name(code):
    return unicodedata.name(chr(code)).split("ORKHON ")[1]


def metrics(letter):
    shape, advance = fitted(letter)
    return {
        "ink_bounds": list(shape.bounds),
        "advance": advance,
        "left": shape.bounds[0],
        "right": advance - shape.bounds[2],
        "ink_centroid_y": shape.centroid.y,
    }


def guides(draw, x, baseline, size, width=330):
    draw.rectangle((x, baseline - size * .510, x + width, baseline), fill="#f5f5f5")
    for height in (700, 510, 0, -190):
        y = baseline - height * size / 1000
        draw.line((x, y, x + width, y), fill="#8d8d8d" if height == 0 else RULE)
        label(draw, (x - 45, y - 8), str(height), 13, GRAY)


def changed_proof():
    image = Image.new("RGB", (1680, 1620), "white")
    draw = ImageDraw.Draw(image)
    label(draw, (65, 35), "NEW ORKHON 0.9 / MEASURED CORRECTIONS", 37, bold=True)
    label(draw, (65, 94), "Same em size and baseline. Shaded band = lowercase body, 510 to 0.", 23, GRAY)
    for x, title in ((425, "BEFORE / 0.8"), (920, "AFTER / 0.9"), (1300, "MEASURED CHANGE")):
        label(draw, (x, 155), title, 21, bold=True)
    notes = [
        ("Body bottom", "+55.55 → +0.03", "Post stays 510 / −190"),
        ("Body bottom", "+128.04 → +0.05", "Posts stay 510 / −190"),
        ("Left sidebearing", "32 → 18 units", "Advance 447 → 433"),
        ("Identical to capital", "Full height: 700", "Same outline + metrics"),
    ]
    for row, (code, note) in enumerate(zip(CODES[:4], notes, strict=True)):
        y = 215 + row * 340
        baseline, size = y + 210, 285
        draw.rectangle((45, y - 10, 1635, y + 315), outline=RULE)
        label(draw, (65, y + 60), name(code), 33, bold=True)
        label(draw, (65, y + 106), f"U+{code:05X}", 20, GRAY)
        for x, path in ((425, OLD), (920, NEW)):
            guides(draw, x, baseline, size)
            glyph(draw, x + 75, baseline, chr(code), path, size,
                  "#909090" if path == OLD else INK)
        for offset, text in enumerate(note):
            label(draw, (1300, y + 58 + offset * 40), text, 20,
                  INK if offset == 1 else GRAY, bold=offset == 1)
        if code == 0x10C1E:
            text = chr(code) * 4
            for x, path in ((425, OLD), (920, NEW)):
                glyph(draw, x + 12, y + 295, text, path, 60)
    label(draw, (65, 1580), "Only these four lowercase records change. Every capital, AN and OQ remain unchanged.", 22, GRAY)
    image.save(ROOT / "feedback-diffs.png")


def unchanged_proof():
    image = Image.new("RGB", (1680, 1360), "white")
    draw = ImageDraw.Draw(image)
    label(draw, (65, 35), "AN / OQ — MEASURE FIRST", 38, bold=True)
    label(draw, (65, 95), "Both glyphs are unchanged in 0.9. Coordinates are font units, not screen pixels.", 22, GRAY)
    for x, code in ((140, 0x10C23), (670, 0x10C3F), (1200, 0x10C2A)):
        label(draw, (x, 170), f"{name(code)} / U+{code:05X}", 23, bold=True)
        guides(draw, x, 450, 360)
        glyph(draw, x + 65, 450, chr(code), NEW, 360)
        label(draw, (x, 545), "Round bounds: −10 to 520", 20)
    label(draw, (65, 605), "AN ink centre: y = 255.04. Body centre: y = 255. No measured vertical displacement.", 24, bold=True)
    draw.line((65, 665, 1615, 665), fill=RULE)
    label(draw, (65, 700), "OQ / U+10C38 — CURRENT, NOT A REDESIGN", 28, bold=True)
    guides(draw, 150, 1080, 440, 340)
    glyph(draw, 220, 1080, chr(0x10C38), NEW, 440)
    for y, text in (
        (790, "Wings begin at y = 185 and meet at the descender, y = −190."),
        (837, "The upper 325 units of the body contain only the isolated pole."),
        (884, "Ink centre y = 138.95: visibly bottom-heavy against the round forms."),
        (976, "REVISED PLAN / SIDEWAYS STUDIES"),
        (1023, "1. Compare ±90° skeleton rotations, with the pole left or right."),
        (1070, "2. Refit the body to 0–510 and re-stroke upright at 82/59."),
        (1117, "3. Compare with AN / AEG / Y and test actual text sizes."),
    ):
        label(draw, (640, y), text, 22, INK if y >= 976 else GRAY, bold=y == 976)
    label(draw, (65, 1288), "Geometry diagnoses the distribution; it does not establish reader performance or historical validity.", 22, GRAY)
    image.save(ROOT / "alignment-analysis.png")


def main():
    old = {letter.code: letter for letter in runpy.run_path(
        str(ROOT / "archive-v08" / "lowercase.py"))["LOWER"]}
    current = {letter.code: letter for letter in LOWER}
    data = {
        f"U+{code:05X}": {
            "name": name(code), "before": metrics(old[code]),
            "after": metrics(current[code]),
        } for code in CODES
    }
    for code in (0x10C3A, 0x10C07):
        for key, source in (("before", old), ("after", current)):
            letter = source[code]
            path = letter.paths[1] if code == 0x10C3A else letter.paths[0].replace(
                "M 130 -190 L 130 510", "M 130 510")
            data[f"U+{code:05X}"][key]["body_min"] = stroke(
                path, letter.stroke_stem, letter.stroke_hair).bounds[1]
    assert geometry(current[0x10C23]).equals(geometry(old[0x10C23]))
    assert geometry(current[0x10C38]).equals(geometry(old[0x10C38]))
    (ROOT / "feedback-measurements.json").write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8")
    changed_proof()
    unchanged_proof()
    print("Rendered feedback-diffs.png, alignment-analysis.png and measured before/after JSON.")


if __name__ == "__main__":
    main()
