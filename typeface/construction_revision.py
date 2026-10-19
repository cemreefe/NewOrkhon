"""Scope, attachment checks and proofs for the Serif construction corrections."""

import json

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, box

from build import LETTERS, ROOT, VERSION, Letter, corner_foot, leg_foot, stroke
from glyph_similarity import outline
from lowercase import LOWER, Lower
from specimen import BOLD, SANS, font

CHANGED = {
    "u10C00", "u10C00.lc",
    "u10C0B", "u10C13", "u10C14", "u10C20", "u10C22", "u10C32",
    "u10C07.lc", "u10C0B.lc", "u10C13.lc", "u10C1A.lc", "u10C1C.lc",
    "u10C20.lc", "u10C22.lc", "u10C24.lc", "u10C32.lc", "u10C3C.lc",
    "u10C22_u10C03.liga", "u10C22_u10C03.lc.liga",
}
BASE = ROOT / "archive-v013" / "NewOrkhonText-Regular.ttf"
CURRENT = ROOT / "NewOrkhonText-Regular.ttf"


def checks():
    before, after = TTFont(BASE), TTFont(CURRENT)
    changed = {
        name for name in before.getGlyphOrder()
        if before["glyf"][name].compile(before["glyf"]) != after["glyf"][name].compile(after["glyf"])
        or before["hmtx"][name] != after["hmtx"][name]
    }
    assert changed == CHANGED, changed ^ CHANGED
    count = 0
    forms: list[Letter | Lower] = [*LETTERS, *LOWER]
    for letter in forms:
        stem = getattr(letter, "stroke_stem", 90)
        hair = getattr(letter, "stroke_hair", 64)
        for x, y, direction in letter.serifs:
            for path in letter.paths:
                foot = leg_foot(path, x, y, direction, stem, hair)
                if foot is None or isinstance(foot, str):
                    continue
                lo, hi = sorted((y + direction * 56, y + direction * 58))
                attachment = foot.intersection(box(-2000, lo, 2000, hi))
                protrusion = attachment.difference(stroke(path, stem, hair).buffer(.6))
                assert protrusion.area < .1, (hex(letter.code), x, y, protrusion.area)
                count += 1
    assert count >= 20
    corner_count = 0
    for letter in forms:
        for x, y, direction in letter.serifs:
            if any(leg_foot(path, x, y, direction, letter.stroke_stem, letter.stroke_hair)
                   is not None for path in letter.paths):
                continue
            for path in letter.paths:
                corner = corner_foot(path, x, y, direction, letter.stroke_stem, letter.stroke_hair)
                if corner is None or isinstance(corner, str):
                    continue
                lo, hi = sorted((y + direction * 56, y + direction * 58))
                attachment = corner.intersection(box(-2000, lo, 2000, hi))
                protrusion = attachment.difference(
                    stroke(path, letter.stroke_stem, letter.stroke_hair).buffer(.6)
                )
                assert protrusion.area < .1, (hex(letter.code), x, y, protrusion.area)
                corner_count += 1
    assert corner_count == 4, corner_count
    previous = TTFont(ROOT / "archive-v015" / "NewOrkhonText-Regular.ttf")
    assert {
        name for name in previous.getGlyphOrder()
        if previous["glyf"][name].compile(previous["glyf"]) != after["glyf"][name].compile(after["glyf"])
        or previous["hmtx"][name] != after["hmtx"][name]
    } == {"u10C00", "u10C00.lc"}
    old_oek = outline(before, "u10C1C.lc").intersection(box(-500, -300, 1000, 420))
    new_oek = outline(after, "u10C1C.lc").intersection(box(-500, -300, 1000, 420))
    assert old_oek.symmetric_difference(new_oek).area / old_oek.area < .001
    old_aek, new_aek = outline(before, "u10C1A.lc"), outline(after, "u10C1A.lc")
    assert len(new_aek.interiors) == 1
    assert Polygon(new_aek.interiors[0]).area > Polygon(old_aek.interiors[0]).area * 1.02
    densities = {}
    for label, tt in (("before", before), ("after", after)):
        shape = outline(tt, "u10C07.lc")
        x0, _, x1, _ = shape.bounds
        body = shape.intersection(box(x0, 0, x1, 510))
        densities[label] = body.area / ((x1 - x0) * 510)
    assert densities["after"] < densities["before"]
    result = {
        "version": VERSION, "base": "0.13", "changed": sorted(changed),
        "unchanged_glyphs": len(before.getGlyphOrder()) - len(changed),
        "tangent_attachments_checked": count, "OE_body_coverage": densities,
        "corner_attachments_checked": corner_count,
        "OEK_lower_tier_area_delta": old_oek.symmetric_difference(new_oek).area,
        "AEK_counter_area_before": Polygon(old_aek.interiors[0]).area,
        "AEK_counter_area_after": Polygon(new_aek.interiors[0]).area,
    }
    (ROOT / "analysis" / "construction-checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"PASS: {len(changed)} changed glyphs; {count} tilted serif attachments; OE weight and OEK lower tier.")
    return result


def proof(filename, title, codes):
    image = Image.new("RGB", (1600, 1080), "white")
    draw = ImageDraw.Draw(image)
    draw.text((88, 48), title, font=font(BOLD, 44), fill="black")
    draw.text((550, 144), "0.13 / BEFORE", font=font(SANS, 20), fill="black")
    draw.text((1080, 144), f"{VERSION} / AFTER", font=font(SANS, 20), fill="black")
    for row, (code, label) in enumerate(codes):
        baseline = 355 + row * 270
        draw.text((88, baseline - 103), label, font=font(SANS, 27), fill="black")
        for column, path in enumerate((BASE, CURRENT)):
            right = 804 + column * 530
            for value in (700, 510, 0, -190):
                y = baseline - value * .23
                draw.line((right - 290, y, right + 10, y), fill="black", width=1)
            draw.text((right, baseline), chr(code), anchor="rs", direction="rtl",
                      font=font(path, 230), features=["ss01"], fill="black")
    image.save(ROOT / "analysis" / filename)


if __name__ == "__main__":
    checks()
    proof("rtl-oe-before-after.png", "RTL shoulders / OE weight",
          [(0x10C24, "AEN"), (0x10C3C, "AER"), (0x10C07, "OE")])
    proof("curved-heads-before-after.png", "Lowercase heads",
          [(0x10C1A, "AEK"), (0x10C1C, "OEK")])
