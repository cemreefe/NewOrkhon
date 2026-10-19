"""Compare traditional Orkhon with New Orkhon Sans lowercase and uppercase."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import fitz
from reportlab.pdfgen import canvas

from deck import (
    INK,
    MONO,
    REFERENCE,
    ROOT,
    SANS_LOWER,
    SANS_UPPER,
    VERSION,
    Slide,
    draw_path_pdf,
    export_svg,
    font_data,
    shape,
)
from showcase import ROWS, WIKI, tr_lower

OUT = ROOT / "word-comparison"
WIDTH, HEIGHT = 2600, 3280
SIZE = 200
LEFT, RIGHT = 100, 2500
TOP, ROW_HEIGHT = 470, 250
COLUMNS = ((540, 1160, REFERENCE), (1210, 1830, SANS_LOWER), (1880, 2500, SANS_UPPER))


@dataclass(frozen=True)
class Word:
    key: str
    position: int
    reading: str
    meaning: str


WORDS = (
    Word("G1", 1, "Teŋri", "Tanrı"),
    Word("G1", 5, "Türk", "Türk"),
    Word("G1", 6, "Bilge", "Bilge · kağan adı"),
    Word("G1", 7, "kagan", "kağan"),
    Word("G2", 25, "bodun", "halk"),
    Word("D1", 10, "kişi", "insan"),
    Word("D1", 6, "yer", "yer"),
    Word("G2", 12, "kün", "gün, güneş"),
    Word("G2", 21, "tün", "gece"),
    Word("D3", 36, "törüg", "töreyi"),
)


def split_words(value: str) -> list[str]:
    return [word.strip() for word in value.split(":") if word.strip()]


def compose() -> tuple[Slide, list[dict[str, Any]]]:
    slide = Slide("New Orkhon / ten inscription words / original, Sans lowercase, Sans uppercase")
    slide.text("NEW ORKHON / YENİ ORHUN", LEFT, 78, 24, font=MONO)
    slide.text(f"WORD COMPARISON / {VERSION}", RIGHT, 78, 24, font=MONO, align="right")
    slide.text("New Orkhon", 94, 224, 118)
    slide.text("Orkhon script reimagined for a modern era.", LEFT, 289, 38)
    slide.line(LEFT, 332, RIGHT, 332, width=2)

    slide.text("LATIN / TÜRKÇE", LEFT, 398, 27, font=MONO)
    for (left, right, _), title, label in zip(
        COLUMNS,
        ("Original", "Sans lowercase", "Sans uppercase"),
        ("Traditional reference", "New Orkhon Sans", "New Orkhon Sans"),
        strict=True,
    ):
        centre = (left + right) / 2
        slide.text(title, centre, 398, 48, align="center")
        slide.text(label, centre, 442, 25, align="center")
    slide.line(LEFT, TOP, RIGHT, TOP, width=2)

    records = []
    for index, sample in enumerate(WORDS):
        row = ROWS[sample.key]
        originals, readings = split_words(row[2]), split_words(row[4])
        assert len(originals) == len(readings)
        word = originals[sample.position - 1]
        source_reading = readings[sample.position - 1]
        assert tr_lower(source_reading) == tr_lower(sample.reading)
        assert all(0x10C00 <= ord(char) <= 0x10C4F for char in word)
        top = TOP + index * ROW_HEIGHT
        baseline = top + 176
        slide.text(f"{index + 1:02d} / {sample.key}", LEFT, top + 47, 22, font=MONO)
        slide.text(sample.reading, LEFT - 2, top + 121, 62)
        slide.text(sample.meaning, LEFT, top + 173, 32)
        runs = []
        for left, right, path in COLUMNS:
            features: dict[str, Any] = {}
            advance, bounds = slide.run(
                word, (left + right) / 2, baseline, SIZE,
                path=path, features=features, align="center",
                name=f"{sample.reading} / {path.stem}",
            )
            assert left <= bounds[0] < bounds[2] <= right, (sample.reading, bounds)
            assert top + 12 < bounds[1] < bounds[3] < top + ROW_HEIGHT - 12
            names = shape(path, word, features)[3]
            if path != REFERENCE:
                expected = [
                    f"u{ord(char):05X}" + (".lc" if path == SANS_LOWER else "")
                    for char in word
                ]
                assert names == expected[::-1], (sample.reading, names, expected)
            runs.append({
                "font": path.name, "em_size": SIZE,
                "case": "lowercase" if path == SANS_LOWER else (
                    "uppercase" if path == SANS_UPPER else "uncased historical reference"
                ),
                "features": features, "glyphs_visual_order": names,
                "advance": advance, "bounds": bounds,
            })
        slide.line(LEFT, top + ROW_HEIGHT, RIGHT, top + ROW_HEIGHT, width=1)
        records.append({
            "source_line": sample.key, "source_word_one_based": sample.position,
            "unicode_spelling_unchanged": word, "source_reading": source_reading,
            "display_reading": sample.reading, "short_turkish_meaning": sample.meaning,
            "runs": runs,
        })

    slide.text(
        "Kül Tigin inscription · G = south face; D = east face · Ten selected words, not a continuous passage.",
        LEFT, 3030, 28,
    )
    slide.text(
        "Original column: Noto Sans Old Turkic, not a stone tracing. The inscription has no uppercase/lowercase.",
        LEFT, 3076, 28,
    )
    slide.text(
        "Same Unicode spelling in all three columns; logical right-to-left shaping. All samples set at the same em size.",
        LEFT, 3122, 28,
    )
    slide.text(
        "Source: Turkish Wikisource contributors / CC BY-SA 4.0 · Short Turkish glosses are editorial.",
        LEFT, 3179, 25,
    )
    slide.text("tr.wikisource.org/wiki/Orhun_Yazıtları_(Kül_Tigin)", LEFT, 3224, 24, font=MONO)
    for element in slide.elements:
        if element["kind"] == "text":
            x0, y0, x1, y1 = element["bounds"]
            assert 75 < x0 < x1 < WIDTH - 75 and 40 < y0 < y1 < HEIGHT - 35, element["text"]
    return slide, records


def export_poster_pdf(slide: Slide, path: Path) -> None:
    pdf = canvas.Canvas(str(path), pagesize=(WIDTH, HEIGHT), invariant=1)
    pdf.setTitle(slide.title)
    pdf.setAuthor("New Orkhon")
    pdf.translate(0, HEIGHT)
    pdf.scale(1, -1)
    pdf.setFillColor(slide.bg)
    pdf.rect(0, 0, WIDTH, HEIGHT, stroke=0, fill=1)
    for element in slide.elements:
        if element["kind"] in ("path", "text"):
            draw_path_pdf(
                pdf, element["commands"], element["color"],
                element.get("stroke"), element.get("width", 1.3),
            )
        else:
            assert element["kind"] == "line"
            pdf.setStrokeColor(INK)
            pdf.setLineWidth(element["width"])
            pdf.line(element["x"], element["y"], element["x2"], element["y2"])
    pdf.showPage()
    pdf.save()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    slide, records = compose()
    stem = OUT / "New-Orkhon-Sans-Case-Comparison"
    export_svg(slide, stem.with_suffix(".svg"), WIDTH, HEIGHT)
    export_poster_pdf(slide, stem.with_suffix(".pdf"))
    with fitz.open(stem.with_suffix(".pdf")) as document:
        assert len(document) == 1 and not document[0].get_images()
        document[0].get_pixmap(alpha=False).save(stem.with_suffix(".png"))
    metadata = {
        "version": VERSION, "size_pixels": [WIDTH, HEIGHT],
        "source": WIKI, "attribution": "Turkish Wikisource contributors / CC BY-SA 4.0",
        "reference_is": "Noto Sans Old Turkic typesetting, not a facsimile of the inscription",
        "new_orkhon_case_is": "Authored lowercase and uppercase, not present in the historical inscription",
        "matched_em_size": SIZE, "word_count": len(records),
        "fonts": {
            path.name: {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "units_per_em": font_data(str(path))[0]["head"].unitsPerEm,
            }
            for _, _, path in COLUMNS
        },
        "words": records,
    }
    (OUT / "sans-case-verification.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(f"PASS: {len(records)} source-verified words; 30 unclipped RTL runs; vector-only PDF.")
    print(stem.with_suffix(".png"))


if __name__ == "__main__":
    main()
