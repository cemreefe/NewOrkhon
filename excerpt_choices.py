"""Render four source-verified alternatives without modifying the production deck."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw, ImageFont

from deck import (
    INK,
    MONO,
    REGULAR,
    SANS_UPPER,
    UPPER,
    VERSION,
    Slide,
    case_ranges,
    export_pdf,
    export_svg,
    font_data,
    shape,
    wrapped_words,
)

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from orkhon import tr_lower  # noqa: E402

SOURCE = json.loads((ROOT / "excerpt-source-rows.json").read_text())
OUT = ROOT / "excerpt-choices"
SIZE = 64
COLUMN_WIDTH = 658


@dataclass(frozen=True)
class Choice:
    letter: str
    key: str
    start: int
    stop: int
    title: str
    capitals: tuple[int, ...]
    periods: tuple[int, ...]
    meaning: str


CHOICES = (
    Choice(
        "A", "G11", 2, 12, "Words on stone", (0, 7), (6, 9),
        "Ne sözüm varsa bengü taşa yazdım. Ona bakarak bilin.",
    ),
    Choice(
        "B", "D27", 1, 17, "Night and day", (0, 7, 8), (6, 15),
        "Türk halkı için gece uyumadım, gündüz oturmadım. "
        "Kardeşim Kül Tigin ve iki şad ile ölesiye çabaladım.",
    ),
    Choice(
        "C", "G2", 10, 28, "The four directions", (0, 12), (11, 17),
        "Doğuda gün doğusuna, güneyde gün ortasına, batıda gün batısına, "
        "kuzeyde gece ortasına kadar, bu sınırlar içindeki halkların hepsi bana tâbi.",
    ),
    Choice(
        "D", "D3", 7, 37, "The rulers and their people",
        (0, 6, 14, 20, 26), (5, 13, 19, 25, 29),
        "Kağanları bilge ve yiğitti; görevlileri de öyleydi. Beyleriyle halkı uyum içindeydi. "
        "Bu yüzden devleti koruyup töreyi düzenlediler.",
    ),
)


def split_words(value: str) -> list[str]:
    return [word.strip() for word in value.split(":") if word.strip()]


def measure(text: str, font: Path, size: float) -> float:
    return shape(font, text, rtl=False)[1] * size / font_data(str(font))[0]["head"].unitsPerEm


def text_lines(text: str, font: Path, size: float, width: float) -> list[str]:
    lines: list[str] = []
    for word in text.split():
        if not lines or measure(lines[-1] + " " + word, font, size) > width:
            lines.append(word)
        else:
            lines[-1] += " " + word
    return lines


def reading(tokens: list[str], choice: Choice) -> str:
    words = [tr_lower(word) for word in tokens]
    for index in choice.capitals:
        word = words[index]
        initial = "İ" if word[0] == "i" else word[0].upper()
        words[index] = initial + word[1:]
    for index in choice.periods:
        words[index] += "."
    return " ".join(words)


def compose(choice: Choice) -> tuple[Slide, dict[str, Any]]:
    row = SOURCE["rows"][choice.key]
    original, latin = split_words(row[2]), split_words(row[4])
    assert len(original) == len(latin)
    raw = original[choice.start:choice.stop]
    words = [word.replace("\U00010c15", "\U00010c14") for word in raw]
    assert words and all(all(0x10C00 <= ord(char) <= 0x10C4F for char in word) for word in words)
    capitals = set(choice.capitals)
    assert max(capitals) < len(words)
    text = " ".join(words)
    features = case_ranges(words, capitals)
    larger_font = max(
        (UPPER, SANS_UPPER), key=lambda font: shape(font, text, features)[1],
    )
    width = COLUMN_WIDTH
    while True:
        groups = wrapped_words(words, larger_font, SIZE, width, 6, capitals)
        if all(
            shape(font, " ".join(group), case_ranges(
                group, {n - start for n in capitals if start <= n < start + len(group)},
            ))[1] * SIZE / 1000 <= COLUMN_WIDTH
            for font in (UPPER, SANS_UPPER) for start, group in groups
        ):
            break
        width -= 8
        assert width > 600
    assert [word for _, group in groups for word in group] == words

    face = "south face" if choice.key.startswith("G") else "east face"
    slide = Slide(f"Option {choice.letter} / Kül Tigin {choice.key}")
    slide.text("NEW ORKHON / EXCERPT CHOICES", 88, 60, 16, font=MONO)
    slide.text(f"OPTION {choice.letter} / 4", 1512, 60, 16, font=MONO, align="right")
    slide.text(f"{choice.letter} / {choice.title}", 84, 143, 65)
    slide.text(
        f"Kül Tigin / {face} / {choice.key} / excerpt / {len(words)} words",
        88, 193, 23,
    )
    slide.line(88, 221, 1512, 221)
    slide.text("SERIF", 88, 258, 16, font=MONO)
    slide.text("SANS", 854, 258, 16, font=MONO)
    slide.line(800, 245, 800, 678, width=.7)
    first_baseline = 490 - (len(groups) - 1) * 34
    runs = []
    for font, left, right in ((UPPER, 88, 746), (SANS_UPPER, 854, 1512)):
        for line, (start, group) in enumerate(groups):
            local_caps = {n - start for n in capitals if start <= n < start + len(group)}
            _, bounds = slide.run(
                " ".join(group), right, first_baseline + line * 68, SIZE, INK,
                font, case_ranges(group, local_caps), "right",
            )
            assert bounds[0] >= left - 1 and bounds[2] <= right + 1, bounds
            assert bounds[1] >= 275 and bounds[3] <= 680, bounds
            runs.append({"font": font.name, "bounds": bounds})
    slide.line(88, 686, 1512, 686)
    slide.text("TÜRKÇE / SHORT MEANING", 88, 713, 13, font=MONO)
    meaning = text_lines(choice.meaning, REGULAR, 25, 1424)
    assert len(meaning) <= 2
    for line, value in enumerate(meaning):
        slide.text(value, 88, 746 + line * 32, 25)
    latin_text = reading(latin[choice.start:choice.stop], choice)
    slide.text("LATIN READING", 88, 812, 12, font=MONO)
    latin_lines = text_lines(latin_text, REGULAR, 18, 1424)
    assert len(latin_lines) <= 2
    for line, value in enumerate(latin_lines):
        slide.text(value, 88, 836 + line * 23, 18)
    slide.text(
        "Wikisource / CC BY-SA 4.0 · Historical spelling; case and line breaks are editorial.",
        88, 888, 14,
    )
    for element in slide.elements:
        if element["kind"] == "text":
            x0, y0, x1, y1 = element["bounds"]
            assert 30 < x0 < x1 < 1570 and 20 < y0 < y1 < 897, element["text"]
    return slide, {
        "option": choice.letter, "key": choice.key,
        "source_word_span_one_based_inclusive": [choice.start + 1, choice.stop],
        "raw_source_words": raw, "rendered_words": words,
        "latin_reading": latin_text, "short_turkish_meaning": choice.meaning,
        "meaning_is": "A shortened modern Turkish rendering, not the source translation verbatim.",
        "editorial_capital_word_indices_zero_based": sorted(capitals),
        "em_size": SIZE, "matched_line_breaks": groups, "runs": runs,
    }


def main() -> None:
    OUT.mkdir(exist_ok=True)
    composed = [compose(choice) for choice in CHOICES]
    slides = [slide for slide, _ in composed]
    pdf = OUT / "New-Orkhon-Excerpt-Choices.pdf"
    export_pdf(slides, pdf)
    document = fitz.open(pdf)
    assert len(document) == 4
    images = []
    for index, (page, slide) in enumerate(zip(document, slides, strict=True)):
        assert len(page.get_images()) == 0
        page.insert_link({
            "kind": fitz.LINK_URI, "from": fitz.Rect(50, 520, 900, 540),
            "uri": SOURCE["url"],
        })
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        image.save(OUT / f"option-{CHOICES[index].letter}.png")
        export_svg(slide, OUT / f"option-{CHOICES[index].letter}.svg")
        images.append(image)
    document.set_metadata({"title": "New Orkhon / Four inscription alternatives", "author": "New Orkhon"})
    document.saveIncr()
    document.close()
    contact = Image.new("RGB", (1968, 1160), "white")
    draw = ImageDraw.Draw(contact)
    label_font = ImageFont.truetype(str(MONO), 21)
    draw.text((24, 16), "A–D / Same type size · Serif left · Sans right", fill="black", font=label_font)
    for index, image in enumerate(images):
        image.thumbnail((960, 540), Image.Resampling.LANCZOS)
        x, y = 16 + index % 2 * 976, 56 + index // 2 * 550
        contact.paste(image, (x, y))
        draw.rectangle((x, y, x + 960, y + 540), outline="black", width=1)
    contact.save(OUT / "New-Orkhon-Excerpt-Choices.png")
    (OUT / "verification.json").write_text(json.dumps({
        "source_url": SOURCE["url"],
        "fonts": f"Unmodified production {VERSION} Serif and Sans",
        "status": "Four proposals; production D1 unchanged",
        "checks": "Exact source spans, glyph coverage, shaping, shared em size and line breaks, bounds, vector PDF.",
        "source_note": "Colons become spaces; Yenisei EZ is mapped to its Orkhon counterpart where present.",
        "license": "Source text: Wikisource contributors, CC BY-SA 4.0; shortened translations and typesetting adapted.",
        "choices": [data for _, data in composed],
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: 4 verified excerpts, 8 matched specimens; vector PDF and full comparison sheet in {OUT}")


if __name__ == "__main__":
    main()
