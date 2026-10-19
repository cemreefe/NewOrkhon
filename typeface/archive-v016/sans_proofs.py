"""Black-and-white alphabet comparisons at one em size and shared baselines."""

import unicodedata

from PIL import Image, ImageDraw

from build import LETTERS, ROOT, VERSION
from specimen import BOLD, SANS, font


def proof(lowercase):
    image = Image.new("RGB", (1600, 1080), "white")
    draw = ImageDraw.Draw(image)
    title = "LOWERCASE" if lowercase else "CAPITALS"
    draw.text((88, 36), f"New Orkhon / {title}", font=font(BOLD, 45), fill="black")
    draw.text((88, 104), f"Serif / Sans · {VERSION} · same Unicode signs",
              font=font(SANS, 23), fill="black")
    suffix = "Lowercase" if lowercase else ""
    serif = font(ROOT / f"NewOrkhonText{suffix}-Regular.ttf", 125)
    sans = font(ROOT / f"NewOrkhonSans{suffix}-Regular.ttf", 125)
    for index, item in enumerate(LETTERS):
        col, row = index % 7, index // 7
        x, baseline = 88 + col * 204, 295 + row * 119
        label = unicodedata.name(chr(item.code)).split("ORKHON ", 1)[1]
        draw.text((x, baseline - 97), label, font=font(SANS, 16), fill="black")
        draw.line((x, baseline, x + 181, baseline), fill="black", width=1)
        for face, centre in ((serif, x + 83), (sans, x + 177)):
            width = ImageDraw.Draw(image).textlength(chr(item.code), font=face, direction="rtl")
            draw.text((centre + width / 2, baseline), chr(item.code), font=face,
                      anchor="rs", direction="rtl", fill="black")
    draw.text((88, 1018), "SERIF / SANS in every cell · same baseline and em size",
              font=font(SANS, 21), fill="black")
    path = ROOT / "analysis" / f"sans-alphabet-{'lowercase' if lowercase else 'capitals'}.png"
    image.save(path)
    print(path)


if __name__ == "__main__":
    proof(False)
    proof(True)
