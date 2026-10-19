"""Compare an uncommitted paired-return AD study against the released alphabet."""

import json

from PIL import Image, ImageDraw
from shapely import affinity

from build import ROOT, fitted
from glyph_similarity import geometry_dice, read_forms
from lowercase import Lower
from specimen import BOLD, SANS, font

PROPOSAL = Lower(
    0x10C11,
    ["M 80 510 C 240 455 240 325 80 255 C 240 185 240 55 80 0",
     "M 320 510 C 480 455 480 325 320 255 C 480 185 480 55 320 0",
     "M 80 255 L 320 255"],
    [], ("open", "round"),
    "Unapplied study: two open serpentine strokes linked at the waist.",
)


def draw_shape(draw, shape, center, baseline, size):
    x0, _, x1, _ = shape.bounds
    factor, offset = size / 1000, center - (x0 + x1) / 2 * size / 1000
    polys = [shape] if shape.geom_type == "Polygon" else list(shape.geoms)
    for poly in polys:
        draw.polygon([(offset + x * factor, baseline - y * factor)
                      for x, y in poly.exterior.coords], fill="black")
        for ring in poly.interiors:
            draw.polygon([(offset + x * factor, baseline - y * factor)
                          for x, y in ring.coords], fill="white")


def main():
    forms = read_forms()
    indexed = {f["glyph"]: f for f in forms}
    candidate, _ = fitted(PROPOSAL)
    x0, _, x1, _ = candidate.bounds
    centered = affinity.translate(candidate, xoff=-(x0 + x1) / 2)
    neighbors = sorted([
        {"glyph": f["glyph"], "score": geometry_dice(centered, f["centered"])}
        for f in forms if f["code"] != PROPOSAL.code
    ], key=lambda f: f["score"], reverse=True)
    current = geometry_dice(indexed["u10C11.lc"]["centered"], indexed["u10C28.lc"]["centered"])
    proposal = geometry_dice(centered, indexed["u10C28.lc"]["centered"])
    result = {
        "applied": False, "metric": "center-aligned vector Dice, not a confusion probability",
        "current_AD_ENC": current, "proposal_AD_ENC": proposal, "nearest": neighbors[:8],
    }
    image = Image.new("RGB", (1600, 920), "white")
    draw = ImageDraw.Draw(image)
    draw.text((88, 48), "AD / ENC", font=font(BOLD, 49), fill="black")
    draw.text((88, 125), "Paired open-return AD study · not applied to the font",
              font=font(SANS, 26), fill="black")
    for center, label, shape in [
        (260, "ENC / CURRENT", indexed["u10C28.lc"]["shape"]),
        (620, "AD / CURRENT", indexed["u10C11.lc"]["shape"]),
        (980, "AD / STUDY", candidate),
        (1340, "ENY / CURRENT", indexed["u10C2A.lc"]["shape"]),
    ]:
        draw.text((center - 150, 230), label, font=font(SANS, 18), fill="black")
        for y in (300, 357, 510, 567):
            draw.line((center - 150, y, center + 150, y), fill="black", width=1)
        draw_shape(draw, shape, center, 510, 300)
        draw_shape(draw, shape, center, 675, 64)
    draw.text((88, 750), f"AD–ENC outline overlap: {current:.0%} current / {proposal:.0%} study",
              font=font(SANS, 24), fill="black")
    draw.text((88, 801), "AD: paired open returns linked at the waist. ENC: tall stem and two closed bowls.",
              font=font(SANS, 22), fill="black")
    draw.text((88, 846), "ENY is shown as a guard: AD cannot simply become another 3.",
              font=font(SANS, 22), fill="black")
    image.save(ROOT / "analysis" / "ad-enc-study.png")
    (ROOT / "analysis" / "ad-enc-study.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
