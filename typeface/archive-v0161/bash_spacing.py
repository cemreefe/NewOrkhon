"""Check and show BASH's placement-only change from release 0.16."""

import json

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

from build import ROOT, VERSION
from shaping_revision import shaped
from specimen import BOLD, SANS, font

BASE = ROOT / "archive-v016"
TARGETS = {"u10C48", "u10C48.lc"}
PROBES = ("𐰃𐱈𐰃", "𐰞𐱈", "𐱈𐰢𐱈")


def checks():
    records = []
    for style in ("Text", "Sans"):
        for default in ("", "Lowercase"):
            filename = f"NewOrkhon{style}{default}-Regular.ttf"
            old, new = TTFont(BASE / filename), TTFont(ROOT / filename)
            changed = set()
            assert old.getBestCmap() == new.getBestCmap()
            assert old.getGlyphOrder() == new.getGlyphOrder()
            for name in old.getGlyphOrder():
                before, after = old["glyf"][name], new["glyf"][name]
                assert old["hmtx"][name][0] == new["hmtx"][name][0], name
                if name not in TARGETS:
                    assert before.compile(old["glyf"]) == after.compile(new["glyf"]), name
                    assert old["hmtx"][name] == new["hmtx"][name], name
                    continue
                coords_before, ends_before, flags_before = before.getCoordinates(old["glyf"])
                coords_after, ends_after, flags_after = after.getCoordinates(new["glyf"])
                assert list(ends_before) == list(ends_after)
                assert list(flags_before) == list(flags_after)
                assert [(x - 12, y) for x, y in coords_before] == list(coords_after), name
                assert new["hmtx"][name][1] == old["hmtx"][name][1] - 12
                advance = new["hmtx"][name][0]
                records.append({
                    "font": filename, "glyph": name, "shift_x": -12,
                    "advance_before_and_after": advance,
                    "left_before": before.xMin, "left_after": after.xMin,
                    "right_before": advance - before.xMax,
                    "right_after": advance - after.xMax,
                })
                changed.add(name)
            assert changed == TARGETS
            for probe in PROBES:
                for features in ({}, {"kern": 0}, {"ss01": 1}, {"ss02": 1}):
                    a = shaped(BASE / filename, probe, features)
                    b = shaped(ROOT / filename, probe, features)
                    assert [(item["name"], item["cluster"]) for item in a] == [
                        (item["name"], item["cluster"]) for item in b
                    ]
    (ROOT / "analysis" / "bash-spacing-checks.json").write_text(json.dumps({
        "version": VERSION, "base": "0.16", "shift_units": -12,
        "shape_changed": False, "advance_changed": False,
        "other_glyphs_changed": False, "measurements": records,
    }, indent=2) + "\n")
    print("PASS: BASH translated exactly -12 units; all advances and other glyphs unchanged in 4 fonts.")


def proof():
    image = Image.new("RGB", (1800, 1610), "white")
    draw = ImageDraw.Draw(image)
    draw.text((65, 32), "BASH / 12 units left inside the same advance", font=font(BOLD, 38), fill="black")
    draw.text((65, 90), "Shape, height and total advance unchanged. Grey guides mark the fixed glyph cell.",
              font=font(SANS, 23), fill="black")
    for index, (style, default, label) in enumerate((
        ("Text", "", "Serif / capital"), ("Text", "Lowercase", "Serif / lowercase"),
        ("Sans", "", "Sans / capital"), ("Sans", "Lowercase", "Sans / lowercase"),
    )):
        y = 158 + index * 344
        filename = f"NewOrkhon{style}{default}-Regular.ttf"
        draw.text((65, y), label, font=font(BOLD, 25), fill="black")
        for column, (directory, version) in enumerate(((BASE, "BEFORE / 0.16"), (ROOT, "AFTER / " + VERSION))):
            x, baseline = 340 + column * 750, y + 225
            face = font(directory / filename, 230)
            tt = TTFont(directory / filename)
            name = tt.getBestCmap()[0x10C48]
            glyph = tt["glyf"][name]
            advance, left = tt["hmtx"][name]
            scale = 230 / 1000
            right = advance - glyph.xMax
            draw.text((x, y), version, font=font(SANS, 18), fill="black")
            draw.rectangle((x, baseline - 175, x + advance * scale, baseline + 8), outline="#999999")
            draw.text((x, baseline), "𐱈", font=face, anchor="ls", direction="rtl", fill="black")
            draw.text((x + 180, y + 73), f"Left: {left}  /  Right: {right}",
                      font=font(SANS, 22), fill="black")
            draw.text((x + 180, y + 110), f"Advance: {advance}",
                      font=font(SANS, 20), fill="black")
            draw.text((x, y + 300), "   ".join(PROBES),
                      font=font(directory / filename, 44), direction="rtl", anchor="ls", fill="black")
        draw.line((65, y + 324, 1735, y + 324), fill="#bbbbbb", width=1)
    draw.text((65, 1565), "RTL spacing probes are synthetic, not inscription excerpts.",
              font=font(SANS, 21), fill="black")
    image.save(ROOT / "analysis" / "bash-spacing-before-after.png")


if __name__ == "__main__":
    checks()
    proof()
