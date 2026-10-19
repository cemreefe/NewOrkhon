"""Pairwise geometry, text-size rasters and optical-density diagnostics.

Input is the compiled release TTF, not the authored path approximation.
Run this file directly; it writes CSV/JSON under analysis/.
"""

import csv
import hashlib
import itertools
import json
import sys
import unicodedata
from pathlib import Path

import numpy as np
import shapely
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from shapely import affinity
from shapely.geometry import GeometryCollection, Polygon, box

from build import VERSION
from lowercase import LOWER

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "analysis"
UPPER = ROOT / "NewOrkhonText-Regular.ttf"
SMALL = ROOT / "NewOrkhonTextLowercase-Regular.ttf"
SIZES = (20, 24, 32, 48)
FRAME = (96, 72)
BASELINE = 52
LOWER_META = {item.code: item for item in LOWER}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def outline(font, name):
    glyph = font["glyf"][name]
    assert not glyph.isComposite(), "Add composite decomposition before analyzing."
    coords, ends, flags = glyph.getCoordinates(font["glyf"])
    assert all(flag & 1 for flag in flags), "Add curve flattening for off-curve points."
    shape = GeometryCollection()
    start = 0
    for end in ends:
        contour = Polygon(coords[start:end + 1])
        assert contour.is_valid and not contour.is_empty
        shape = shape.symmetric_difference(contour)
        start = end + 1
    assert shape.is_valid and shape.area > 0
    return shape


def read_forms():
    upper, lower = TTFont(UPPER), TTFont(SMALL)
    assert upper["head"].unitsPerEm == lower["head"].unitsPerEm == 1000
    codes = sorted(LOWER_META)
    result = []
    for case, font in (("upper", upper), ("lower", lower)):
        for code in codes:
            name = font.getBestCmap()[code]
            shape = outline(font, name)
            x0, y0, x1, y1 = shape.bounds
            centered = affinity.translate(shape, xoff=-(x0 + x1) / 2)
            normalized = affinity.scale(
                affinity.translate(centered, yoff=-y0),
                xfact=700 / (y1 - y0), yfact=700 / (y1 - y0), origin=(0, 0),
            )
            polygons = [shape] if shape.geom_type == "Polygon" else list(shape.geoms)
            result.append({
                "id": f"{case}-{code:05X}", "code": code, "case": case,
                "name": unicodedata.name(chr(code)).split("ORKHON ")[1],
                "glyph": name, "shape": shape, "centered": centered,
                "normalized": normalized, "advance": font["hmtx"][name][0],
                "bounds": list(shape.bounds),
                "nominal_stem": 90 if case == "upper" else LOWER_META[code].stroke_stem,
                "holes": [Polygon(ring) for p in polygons for ring in p.interiors],
            })
    assert len(result) == 84
    return result


def raster(form, size):
    path = UPPER if form["case"] == "upper" else SMALL
    font = ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)
    image = Image.new("L", FRAME, 0)
    x0, _, x1, _ = form["bounds"]
    origin = FRAME[0] / 2 - (x0 + x1) / 2 * size / 1000
    ImageDraw.Draw(image).text(
        (origin, BASELINE), chr(form["code"]), font=font,
        fill=255, anchor="ls", direction="rtl",
    )
    bounds = image.getbbox()
    assert bounds is not None
    x0, y0, x1, y1 = bounds
    assert x0 > 0 and y0 > 0 and x1 < FRAME[0] and y1 < FRAME[1], form["id"]
    return image


def rle(image):
    return [[len(list(group)), int(value)] for value, group in
            itertools.groupby(np.asarray(image).reshape(-1))]


def dice_matrices(forms):
    scores: dict[int, np.ndarray] = {}
    blurred: dict[int, np.ndarray] = {}
    rasters: dict[int, list[Image.Image]] = {}
    for size in SIZES:
        images = [raster(form, size) for form in forms]
        rasters[size] = images
        for target, buffers in (
            (scores, images),
            (blurred, [image.filter(ImageFilter.GaussianBlur(size / 24)) for image in images]),
        ):
            alpha = np.asarray([np.asarray(image).reshape(-1) for image in buffers],
                               dtype=np.float64) / 255
            energy = np.square(alpha).sum(axis=1)
            matrix = 2 * (alpha @ alpha.T) / (energy[:, None] + energy[None, :])
            assert np.allclose(matrix.diagonal(), 1)
            assert matrix.min() >= 0 and matrix.max() <= 1 + 1e-12
            target[size] = np.minimum(matrix, 1)
    return scores, blurred, rasters


def geometry_dice(a, b):
    return 2 * a.intersection(b).area / (a.area + b.area)


def csv_write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def pairs():
    OUT.mkdir(exist_ok=True)
    forms = read_forms()
    scores, blurred, rasters = dice_matrices(forms)
    rows = []
    for i, a in enumerate(forms):
        for j in range(i + 1, len(forms)):
            b = forms[j]
            same = a["code"] == b["code"]
            group = "counterparts" if same else (
                a["case"] if a["case"] == b["case"] else "mixed"
            )
            row = {
                "a": a["id"], "b": b["id"], "a_name": a["name"], "b_name": b["name"],
                "group": group, "same_character": same,
                "outline_dice": geometry_dice(a["centered"], b["centered"]),
                "normalized_dice": geometry_dice(a["normalized"], b["normalized"]),
                "outline_hausdorff_em": a["centered"].boundary.hausdorff_distance(
                    b["centered"].boundary) / 1000,
                **{f"raster_{size}": float(scores[size][i, j]) for size in SIZES},
                **{f"blur_{size}": float(blurred[size][i, j]) for size in SIZES},
                "raster_mean": float(np.mean([scores[size][i, j] for size in SIZES])),
                "blur_mean": float(np.mean([blurred[size][i, j] for size in SIZES])),
                "exact_outline": a["centered"].equals(b["centered"]),
            }
            rows.append(row)
        if i % 14 == 0:
            print(f"Compared form {i + 1}/84", flush=True)
    assert len(rows) == 3486
    assert sum(not row["same_character"] for row in rows) == 3444
    exact = [row for row in rows if row["exact_outline"]]
    assert len(exact) == 1 and exact[0]["same_character"] and exact[0]["a_name"] == "AQ"
    for row in rows:
        for key in ("outline_dice", "normalized_dice", "raster_mean", "blur_mean"):
            assert 0 <= row[key] <= 1 + 1e-9
    csv_write(OUT / "glyph-pairs.csv", rows)
    public = []
    for number, form in enumerate(forms):
        public.append({
            key: value for key, value in form.items()
            if key not in ("shape", "centered", "normalized", "holes")
        } | {
            "polygons": [
                [list(map(list, p.exterior.coords))]
                + [list(map(list, ring.coords)) for ring in p.interiors]
                for p in ([form["centered"]] if form["centered"].geom_type == "Polygon"
                          else list(form["centered"].geoms))
            ],
            "raster": {str(size): rle(rasters[size][number]) for size in SIZES},
        })
    dataset = {
        "version": VERSION,
        "font_hashes": {path.name: sha(path) for path in (UPPER, SMALL)},
        "raster_sizes": SIZES, "frame": FRAME, "baseline_px": BASELINE,
        "forms": public, "pairs": rows,
    }
    (OUT / "glyph-analysis.json").write_text(json.dumps(dataset, separators=(",", ":")))
    for group in ("lower", "upper", "mixed"):
        top = sorted([row for row in rows if row["group"] == group],
                     key=lambda row: row["raster_mean"], reverse=True)[:12]
        print("\n", group.upper(), flush=True)
        for row in top:
            print(row["a"], row["b"], row["a_name"], row["b_name"],
                  f"raster={row['raster_mean']:.3f} outline={row['outline_dice']:.3f} "
                  f"blur={row['blur_mean']:.3f} normalized={row['normalized_dice']:.3f}")
    print("Saved all 3,486 pairs and all native raster buffers.")


def blurred_core(form):
    size, count, padding, baseline = 24, 10, 5, 29
    path = UPPER if form["case"] == "upper" else SMALL
    font = ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)
    advance = form["advance"] * size / 1000
    image = Image.new("L", (int(np.ceil(advance * count)) + padding * 2, 44), 0)
    ImageDraw.Draw(image).text(
        (padding, baseline), chr(form["code"]) * count,
        font=font, fill=255, anchor="ls", direction="rtl",
    )
    blurred = np.asarray(image.filter(ImageFilter.GaussianBlur(1)), dtype=float) / 255
    body = 700 if form["case"] == "upper" else 510
    y, x = np.arange(image.height), np.arange(image.width)
    yw = np.maximum(0, np.minimum(y + 1, baseline) -
                    np.maximum(y, baseline - body * size / 1000))
    xw = np.maximum(0, np.minimum(x + 1, padding + 8 * advance) -
                    np.maximum(x, padding + 2 * advance))
    weight = yw[:, None] * xw[None, :]
    return float(((blurred >= .5) * weight).sum() / weight.sum() * 100)


def density():
    forms = read_forms()
    rows = []
    for form in forms:
        shape = form["shape"]
        height = 700 if form["case"] == "upper" else 510
        band = box(-2000, 0, 2000, height)
        disk = shapely.maximum_inscribed_circle(shape, tolerance=.5)
        diameter = disk.length * 2
        hole_diameters = [
            shapely.maximum_inscribed_circle(hole, tolerance=.5).length * 2
            for hole in form["holes"]
        ]
        rows.append({
            "id": form["id"], "case": form["case"], "name": form["name"],
            "code": form["code"], "advance": form["advance"],
            "body_ink_pct": shape.intersection(band).area / (form["advance"] * height) * 100,
            "line_ink_pct": shape.area / (form["advance"] * 1000) * 100,
            "bbox_ink_pct": shape.area / box(*shape.bounds).area * 100,
            "effective_stroke": 2 * shape.area / shape.length,
            "max_ink_diameter": diameter,
            "peak_over_nominal": diameter / form["nominal_stem"],
            "nominal_stem": form["nominal_stem"],
            "circle_x": disk.coords[0][0] - (shape.bounds[0] + shape.bounds[2]) / 2,
            "circle_y": disk.coords[0][1],
            "closed_counters": len(form["holes"]),
            "smallest_counter_diameter": min(hole_diameters) if hole_diameters else None,
            "blurred_core_pct": blurred_core(form),
        })
    for case in ("upper", "lower"):
        group = [row for row in rows if row["case"] == case]
        values = np.asarray([row["body_ink_pct"] for row in group])
        median = float(np.median(values))
        mad = float(np.median(np.abs(values - median)))
        for row in group:
            row["body_vs_case_median"] = row["body_ink_pct"] / median
            row["body_robust_z"] = .67448975 * (row["body_ink_pct"] - median) / mad
        print("\n", case, "body median", round(median, 2), flush=True)
        for metric in ("body_ink_pct", "peak_over_nominal", "blurred_core_pct"):
            print(metric)
            for row in sorted(group, key=lambda item: item[metric], reverse=True)[:10]:
                print(row["name"], round(row["body_ink_pct"], 1),
                      "peak", round(row["max_ink_diameter"], 1),
                      "ratio", round(row["peak_over_nominal"], 2),
                      "blur core", round(row["blurred_core_pct"], 1),
                      "counter", row["smallest_counter_diameter"])
    assert len(rows) == 84
    csv_write(OUT / "glyph-density.csv", rows)
    dataset = json.loads((OUT / "glyph-analysis.json").read_text())
    dataset["density"] = rows
    (OUT / "glyph-analysis.json").write_text(json.dumps(dataset, separators=(",", ":")))
    assert dataset["font_hashes"] == {path.name: sha(path) for path in (UPPER, SMALL)}
    print("Saved 84 density records; source font hashes unchanged.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "density":
        density()
    else:
        pairs()
