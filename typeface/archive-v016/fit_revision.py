"""Compare naturally fitted Sans routes with release 0.15's box-trimmed outlines."""

import json
import runpy
import unicodedata

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw
from shapely.geometry import box
from shapely.ops import unary_union

from build import LETTERS, ROOT, VERSION, constructed, ink_strokes, stroke
from lowercase import LOWER
from sans import sans_forms
from specimen import BOLD, SANS, font


def checks():
    records = []
    old_forms = runpy.run_path(str(ROOT / "archive-v015" / "sans.py"))["sans_forms"](LETTERS, LOWER)
    for case, group, old_group in zip(("capital", "lowercase"), sans_forms(LETTERS, LOWER),
                                      old_forms, strict=True):
        for item, old_item in zip(group, old_group, strict=True):
            assert (item.stroke_stem, item.stroke_hair) == (old_item.stroke_stem, old_item.stroke_hair)
            bottom = getattr(item, "bottom", 0) - (10 if item.round_bottom else 0)
            top = getattr(item, "top", 700) + (10 if item.round_top else 0)
            raw = unary_union([
                stroke(path, old_item.stroke_stem, old_item.stroke_hair,
                       tuple(r[1:] for r in old_item.reliefs if r[0] == i),
                       getattr(old_item, "stroke_join", "round"))
                for i, path in enumerate(old_item.paths)
            ])
            before_clip_bottom = getattr(item, "bottom", 0) if not item.round_bottom else -2000
            before_clip_top = getattr(item, "top", 700) if not item.round_top else 2000
            removed = raw.difference(box(-2000, before_clip_bottom, 2000, before_clip_top)).area
            after = constructed(item)
            assert bottom - .001 <= after.bounds[1] <= bottom + .001
            assert top - .001 <= after.bounds[3] <= top + .001
            for route in ink_strokes(item):
                assert route.difference(after).area < .001
            records.append({
                "codepoint": f"U+{item.code:05X}", "case": case,
                "ink_area_removed_by_previous_crop": round(removed, 3),
                "ink_area_removed_by_current_crop": 0,
                "bounds": list(after.bounds),
            })
    changes = {}
    for style in ("Text", "Sans"):
        filename = f"NewOrkhon{style}-Regular.ttf"
        old, new = TTFont(ROOT / "archive-v015" / filename), TTFont(ROOT / filename)
        changes[style] = [
            name for name in old.getGlyphOrder()
            if old["glyf"][name].compile(old["glyf"]) != new["glyf"][name].compile(new["glyf"])
            or old["hmtx"][name] != new["hmtx"][name]
        ]
    assert set(changes["Text"]) == {"u10C00", "u10C00.lc"}
    output = {
        "version": VERSION, "forms": len(records),
        "previously_cropped_forms": sum(row["ink_area_removed_by_previous_crop"] > 1 for row in records),
        "outline_y_scaling": False, "bounding_box_crop": False,
        "changes_from_0.15": changes, "measurements": records,
    }
    (ROOT / "analysis" / "ink-fitting-checks.json").write_text(json.dumps(output, indent=2) + "\n")
    print(f"PASS: {len(records)} naturally fitted Sans forms; no box crop or outline y-scaling.")


def proof():
    image = Image.new("RGB", (1800, 1260), "white")
    draw = ImageDraw.Draw(image)
    draw.text((65, 32), "Sans / stroke-aware height fitting", font=font(BOLD, 38), fill="black")
    draw.text((65, 88), "Sans / before 0.15 · after " + VERSION,
              font=font(SANS, 24), fill="black")
    examples = [
        (0x10C32, False), (0x10C0D, True), (0x10C14, True),
        (0x10C03, True), (0x10C1C, True), (0x10C31, True),
    ]
    for index, (code, lower) in enumerate(examples):
        x, y = 65 + (index % 3) * 585, 160 + (index // 3) * 535
        label = unicodedata.name(chr(code)).split("ORKHON ")[1]
        draw.text((x, y), label + (" / lowercase" if lower else " / capital"),
                  font=font(BOLD, 23), fill="black")
        for column, (directory, label) in enumerate(((ROOT / "archive-v015", "BEFORE"), (ROOT, "AFTER"))):
            left = x + column * 265
            draw.text((left, y + 52), label, font=font(SANS, 17), fill="black")
            filename = f"NewOrkhonSans{'Lowercase' if lower else ''}-Regular.ttf"
            face = font(directory / filename, 350)
            width = draw.textlength(chr(code), font=face, direction="rtl")
            draw.text((left + (240 - width) / 2, y + 360), chr(code),
                      font=face, anchor="ls", direction="rtl", fill="black")
            for size, offset in ((24, 45), (32, 110), (48, 175)):
                draw.text((left + offset, y + 470), chr(code), font=font(directory / filename, size),
                          anchor="ms", direction="rtl", fill="black")
        draw.line((x, y + 360, x + 510, y + 360), fill="black", width=1)
    image.save(ROOT / "analysis" / "ink-fitting-before-after.png")


if __name__ == "__main__":
    checks()
    proof()
