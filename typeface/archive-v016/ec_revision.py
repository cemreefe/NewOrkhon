"""Render the focused EC revision at a common em size and baseline."""

from PIL import Image, ImageDraw

from build import ROOT
from specimen import BOLD, SANS, font


def proof():
    image = Image.new("RGB", (1600, 880), "white")
    draw = ImageDraw.Draw(image)
    draw.text((88, 48), "EC / U+10C32", font=font(BOLD, 49), fill="black")
    draw.text((88, 123), "New Orkhon 0.13 · capital lambda and raised lowercase",
              font=font(SANS, 26), fill="black")
    rows = [
        ("0.12 / CAPITAL", ROOT / "archive-v012" / "NewOrkhonText-Regular.ttf", []),
        ("0.13 / CAPITAL", ROOT / "archive-v013" / "NewOrkhonText-Regular.ttf", []),
        ("0.12 / LOWERCASE", ROOT / "archive-v012" / "NewOrkhonText-Regular.ttf", ["ss01"]),
        ("0.13 / LOWERCASE", ROOT / "archive-v013" / "NewOrkhonText-Regular.ttf", ["ss01"]),
    ]
    for index, (label, path, features) in enumerate(rows):
        x = 88 + 364 * index
        draw.text((x, 223), label, font=font(SANS, 18), fill="black")
        for y in (340, 416, 620, 696):
            draw.line((x, y, x + 310, y), fill="black", width=1)
        draw.text((x + 287, 620), "𐰲", font=font(path, 400), anchor="rs",
                  direction="rtl", features=features, fill="black")
    draw.text((88, 757), "Guides: cap 700 / body 510 / baseline 0 / descender -190",
              font=font(SANS, 22), fill="black")
    draw.text((88, 806), "Lowercase: identical outline and advance, translated up exactly 190 units.",
              font=font(SANS, 22), fill="black")
    output = ROOT / "analysis" / "ec-before-after.png"
    image.save(output)
    print(output)


if __name__ == "__main__":
    proof()
