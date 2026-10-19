"""Unapplied mirrored-alpha EM study; the production family is not modified."""

import json
from dataclasses import replace

import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw
from shapely import set_precision

from build import LETTERS, ROOT, SIDES, VERSION, fitted, to_glyph
from lowercase import LOWER
from sans import SANS_SIDES, sans_forms
from specimen import BOLD, SANS, font

OUT = ROOT / "studies" / "em-mirrored-alpha"
ALPHA_CAP = (
    "M 80 700 C 95 575 160 510 230 350 C 305 125 360 32 425 32 "
    "C 590 32 590 668 425 668 C 315 668 255 505 195 350 C 110 125 85 125 55 0"
)
ALPHA_LOWER = (
    "M 80 510 C 95 415 160 370 230 255 C 305 90 360 30 425 30 "
    "C 590 30 590 480 425 480 C 315 480 255 370 195 255 C 110 90 85 90 55 0"
)


def build_study(style):
    filename = f"NewOrkhon{'Text' if style == 'Serif' else 'Sans'}-Regular.ttf"
    face = TTFont(ROOT / filename)
    face.recalcTimestamp = False
    family = f"New Orkhon EM Alpha {style} Study"
    for record in face["name"].names:
        label = {
            1: family, 3: family + " " + VERSION, 4: family + " Regular",
            6: f"NewOrkhonEMAlpha{style}Study-Regular", 16: family,
        }.get(record.nameID)
        if label is not None:
            record.string = label.encode(record.getEncoding())
    capital, lower = (LETTERS, LOWER) if style == "Serif" else sans_forms(LETTERS, LOWER)
    for group, suffix, route, top in (
        (capital, "", ALPHA_CAP, 700), (lower, ".lc", ALPHA_LOWER, 510),
    ):
        source = next(g for g in group if g.code == 0x10C22)
        candidate = replace(
            source, paths=[route], serifs=[(80, top, -1), (55, 0, 1)] if style == "Serif" else [],
            reliefs=((0, 210, 255 if suffix else 350, 100, .7),),
            sides=("round", "round"), ink_zone=style == "Sans",
            decision="Unapplied mirrored-alpha study: right loop, crossing, two serifed ends and no tail.",
            **({"bottom": 0} if suffix else {}),
        )
        shape, advance = fitted(candidate, SANS_SIDES if style == "Sans" else SIDES)
        assert shape.geom_type == "Polygon" and len(shape.interiors) == 1
        assert abs(shape.bounds[1]) < .001 and abs(shape.bounds[3] - top) < .001
        name = f"u10C22{suffix}"
        shape = set_precision(shape, grid_size=1).simplify(.3, preserve_topology=True)
        face["glyf"][name] = to_glyph(shape)
        face["hmtx"][name] = advance, round(shape.bounds[0])
    target = OUT / f"EM-Alpha-{style}-Study.ttf"
    face.save(target)
    return target


def mask(path, code, lower):
    image = Image.new("L", (150, 180))
    draw = ImageDraw.Draw(image)
    draw.text((75, 140), chr(code), font=font(path, 120), anchor="ms",
              direction="rtl", features=["ss01"] if lower else [], fill=255)
    return np.asarray(image) / 255


def compare(study, style):
    base = ROOT / f"NewOrkhon{'Text' if style == 'Serif' else 'Sans'}-Regular.ttf"
    records = []
    for lower in (False, True):
        alpha = mask(study, 0x10C22, lower)
        neighbors = []
        for letter in LETTERS:
            if letter.code == 0x10C22:
                continue
            other = mask(base, letter.code, lower)
            score = float(np.minimum(alpha, other).sum() / np.maximum(alpha, other).sum())
            neighbors.append((letter.code, score))
        neighbors.sort(key=lambda row: row[1], reverse=True)
        records.append({
            "case": "lowercase" if lower else "capital",
            "nearest_three": [
                {"codepoint": f"U+{code:05X}", "raster_intersection_over_union": round(score, 4)}
                for code, score in neighbors[:3]
            ],
            "AG": round(next(score for code, score in neighbors if code == 0x10C0D), 4),
            "BASH": round(next(score for code, score in neighbors if code == 0x10C48), 4),
        })
    return records


def proof(serif, sans):
    image = Image.new("RGB", (1800, 1450), "white")
    draw = ImageDraw.Draw(image)
    draw.text((70, 30), "EM / serifed mirrored alpha", font=font(BOLD, 40), fill="black")
    draw.text((70, 90), "Revised proposal / two serifed terminals / no descender",
              font=font(SANS, 23), fill="black")
    for column, label in enumerate(("TRADITIONAL", "CURRENT", "MIRRORED ALPHA", "NEIGHBORS / AG · BASH")):
        draw.text((70 + column * 430, 155), label, font=font(BOLD, 19), fill="black")
    reference = ROOT / "NotoSansOldTurkic-Regular.ttf"
    for row, (style, lower, study) in enumerate((
        ("Serif", False, serif), ("Serif", True, serif), ("Sans", True, sans),
    )):
        baseline = 480 + row * 390
        draw.text((70, baseline - 250), style + (" / lowercase" if lower else " / capital"),
                  font=font(SANS, 19), fill="black")
        base = ROOT / f"NewOrkhon{'Text' if style == 'Serif' else 'Sans'}-Regular.ttf"
        for column, path in enumerate((reference, base, study)):
            features = ["ss01"] if lower and column else []
            draw.text((240 + column * 430, baseline), "𐰢", font=font(path, 330),
                      anchor="ms", direction="rtl", features=features, fill="black")
            if column:
                for size, dx in ((24, -60), (32, 0), (48, 60)):
                    draw.text((240 + column * 430 + dx, baseline + 125), "𐰢",
                              font=font(path, size), anchor="ms", direction="rtl",
                              features=features, fill="black")
        for code, dx in ((0x10C0D, 0), (0x10C48, 180)):
            draw.text((1420 + dx, baseline), chr(code), font=font(base, 215),
                      anchor="ms", direction="rtl", features=["ss01"] if lower else [], fill="black")
    draw.text((70, 1395), "Same em size and baseline / letter labels are above their forms",
              font=font(SANS, 20), fill="black")
    image.save(ROOT / "analysis" / "em-mirrored-alpha-study.png")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    serif, sans = build_study("Serif"), build_study("Sans")
    result = {"status": "unapplied", "diagnostic": "Centered, same-em grayscale raster IoU; not reader confusion.",
              "Serif": compare(serif, "Serif"), "Sans": compare(sans, "Sans")}
    (ROOT / "analysis" / "em-alpha-checks.json").write_text(json.dumps(result, indent=2) + "\n")
    proof(serif, sans)
    print(json.dumps(result, indent=2))
