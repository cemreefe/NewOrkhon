"""0.11: restore AR and reconstruct AT; preserve all other glyph records."""

import json
import sys
from dataclasses import replace
from hashlib import sha256

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from build import LETTERS, ROOT, Letter, fitted, to_glyph
from lowercase import LOWER, Lower

BASE = ROOT / "archive-v010"
OUT = ROOT / "analysis"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TUTA = "𐱃𐰆𐱃𐰀"
EXPECTED = {"u10C43", "u10C43.lc", "u10C3A.lc"}


def text(draw, xy, value, size=23, color="#171717", bold=False):
    draw.text(xy, value, fill=color, font=ImageFont.truetype(BOLD if bold else SANS, size))


def font(path, size):
    return ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)


def sign(draw, path, code, x, y, size, color="#171717"):
    face = font(path, size)
    left, _, right, _ = face.getbbox(chr(code), anchor="ls", direction="rtl")
    draw.text((x - (left + right) / 2, y), chr(code), font=face,
              anchor="ls", direction="rtl", fill=color)


def slanted_studies():
    directory = ROOT / "studies" / "at-slanted"
    directory.mkdir(parents=True, exist_ok=True)
    for lower_default in (False, True):
        filename = f"NewOrkhonText{'Lowercase' if lower_default else ''}-Regular.ttf"
        face = TTFont(ROOT / filename)
        variants: tuple[tuple[Letter | Lower, str, str], ...] = (
            (next(g for g in LETTERS if g.code == 0x10C43), "", "M -20 602 L 440 668"),
            (next(g for g in LOWER if g.code == 0x10C43), ".lc", "M -15 610 L 405 670.5"),
        )
        for source, suffix, arm in variants:
            paths = list(source.paths)
            paths[1] = arm
            shape, advance = fitted(replace(source, paths=paths))
            name = "u10C43" + suffix
            face["glyf"][name] = to_glyph(shape)
            face["hmtx"][name] = (advance, round(shape.bounds[0]))
        face.recalcTimestamp = False
        face.save(directory / filename)
    return directory


def proof():
    slanted = slanted_studies()
    image = Image.new("RGB", (1500, 1660), "white")
    draw = ImageDraw.Draw(image)
    text(draw, (50, 25), "NEW ORKHON / AR RESTORED, AT RECONSTRUCTED", 32, bold=True)
    text(draw, (50, 76), "Both t signs in tuta are AT / U+10C43. AET is unchanged. Top-piece overhang separates AT from AY.", 21)
    for i, (lower, title) in enumerate(((False, "AT / CAPITAL"), (True, "AT / LOWERCASE"))):
        y = 140 + i * 420
        filename = f"NewOrkhonText{'Lowercase' if lower else ''}-Regular.ttf"
        text(draw, (50, y), title, 26, bold=True)
        for j, (directory, label, color) in enumerate((
            (BASE, "Before / symmetric roof + eye", "#777777"),
            (ROOT, "Selected / horizontal top", "#171717"),
            (slanted, "Study / slanted top", "#171717"),
        )):
            x = 260 + j * 490
            baseline = y + 245
            draw.line((x - 160, baseline, x + 160, baseline), fill="#cccccc")
            if lower:
                draw.line((x - 160, baseline - 510 * .27, x + 160, baseline - 510 * .27),
                          fill="#dddddd")
            sign(draw, directory / filename, 0x10C43, x, baseline, 270, color)
            text(draw, (x - 195, y + 285), label, 20, color)
            draw.text((x - 100, y + 330), TUTA, font=font(directory / filename, 60),
                      direction="rtl", fill=color)
    y = 1000
    text(draw, (50, y), "LOWERCASE AR / EXACT RESTORE TO 0.9.1", 25, bold=True)
    for j, (directory, label) in enumerate((
        (BASE, "0.10 / rejected taper"),
        (ROOT, "0.11 / restored"),
        (ROOT / "archive-v091", "0.9.1 / reference"),
    )):
        x, baseline = 260 + j * 490, y + 225
        draw.line((x - 160, baseline, x + 160, baseline), fill="#cccccc")
        sign(draw, directory / "NewOrkhonTextLowercase-Regular.ttf", 0x10C3A, x, baseline, 260)
        text(draw, (x - 185, y + 295), label, 20)
    text(draw, (50, 1360), "TUTA / ACTUAL LOWERCASE RASTERS", 24, bold=True)
    for i, size in enumerate((20, 24, 32, 48)):
        y = 1410 + i * 48
        text(draw, (50, y), f"{size} px", 18)
        for j, directory in enumerate((BASE, ROOT, slanted)):
            draw.text((200 + j * 490, y), TUTA,
                      font=font(directory / "NewOrkhonTextLowercase-Regular.ttf", size),
                      direction="rtl", fill="#171717")
    text(draw, (50, 1630), "Same em scale and logical RTL. The body becomes one side bowl; the roof becomes an arm. Authored design, not recovered history.", 17)
    image.save(OUT / "ar-at-before-after.png")


def validate_scope():
    previous, current = [TTFont(p / "NewOrkhonText-Regular.ttf") for p in (BASE, ROOT)]
    changed = {
        name for name in current.getGlyphOrder()
        if previous["glyf"][name].compile(previous["glyf"]) != current["glyf"][name].compile(current["glyf"])
        or previous["hmtx"][name] != current["hmtx"][name]
    }
    assert changed == EXPECTED, changed
    old = TTFont(ROOT / "archive-v091" / "NewOrkhonText-Regular.ttf")
    name = "u10C3A.lc"
    assert current["glyf"][name].compile(current["glyf"]) == old["glyf"][name].compile(old["glyf"])
    assert current["hmtx"][name] == old["hmtx"][name]
    (OUT / "changed-glyphs-011.json").write_text(json.dumps(sorted(changed), indent=2) + "\n")
    print("Exact scope verified:", sorted(changed))


def measurements():
    current = json.loads((OUT / "glyph-analysis.json").read_text())
    baseline = json.loads((BASE / "glyph-analysis.json").read_text())
    for directory, data in ((ROOT, current), (BASE, baseline)):
        for filename, digest in data["font_hashes"].items():
            assert sha256((directory / filename).read_bytes()).hexdigest() == digest
    result = {}
    for case in ("upper", "lower"):
        identifier = f"{case}-10C43"
        nearest = sorted(
            [p for p in current["pairs"]
             if p["group"] == case and identifier in (p["a"], p["b"])],
            key=lambda p: p["raster_mean"], reverse=True,
        )[:5]
        result[case] = {
            "nearest": nearest,
            "before_density": next(r for r in baseline["density"] if r["id"] == identifier),
            "after_density": next(r for r in current["density"] if r["id"] == identifier),
        }
        print(case, "AT nearest:", [(p["b_name"] if p["a"] == identifier else p["a_name"],
                                     round(p["raster_mean"] * 100, 1)) for p in nearest])
    (OUT / "at-measurements.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    from build import VERSION
    if VERSION != "0.11":
        raise SystemExit("Historical 0.11 proofs are archived in archive-v011; use shaping_revision.py.")
    validate_scope()
    proof()
    if "--measure" in sys.argv:
        measurements()
