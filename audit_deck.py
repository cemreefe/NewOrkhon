"""Verify the generated monochrome deck and editable artwork without a browser."""

import json
from collections import Counter
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import fitz

from deck import OUT, TOTAL, H, W, blueprint_catalog, compose, historical


def check():
    slides, plates = compose(), blueprint_catalog()
    assert len(slides) == TOTAL == 14 and len(plates) == 14
    path_count = 0
    for slide in [*slides, *plates]:
        assert slide.bg in ("#000000", "#FFFFFF")
        for element in slide.elements:
            for key in ("color", "stroke"):
                assert element.get(key) in (None, "#000000", "#FFFFFF")
            if element["kind"] in ("path", "text"):
                commands = element["commands"]
                xs = [row[i] for row in commands for i in range(1, len(row), 2)]
                ys = [row[i] for row in commands for i in range(2, len(row), 2)]
                assert 0 <= min(xs) <= max(xs) <= W, (slide.title, element.get("text"))
                assert 0 <= min(ys) <= max(ys) <= H, (slide.title, element.get("text"))
                if element.get("stroke"):
                    assert 0 < element["width"] <= 2
                path_count += element["kind"] == "path"
    original = " ".join(historical("D1")["words"])
    for slide in slides[:2]:
        actual = " ".join(e["source"] for e in slide.elements if e["kind"] == "path")
        assert actual == original, slide.title
    for filename, length in [
        ("New-Orkhon.pdf", 14), ("New-Orkhon-Blueprints.pdf", 5), ("New-Orkhon-Outlines.pdf", 14),
    ]:
        with fitz.open(OUT / filename) as document:
            assert len(document) == length
            assert all(not page.get_images() for page in document)
    for style in ("serif", "sans"):
        paths = list((OUT / "glyph-outlines" / style).glob("*.svg"))
        assert len(paths) == 84
        for path in paths:
            root = ET.fromstring(path.read_text())
            assert root.tag.endswith("svg")
            assert "<image" not in path.read_text()
    native_shapes = 0
    text_boxes = 0
    with ZipFile(OUT / "New-Orkhon.pptx") as archive:
        assert not any(name.startswith("ppt/media/") for name in archive.namelist())
        parts = [name for name in archive.namelist()
                 if name.startswith("ppt/slides/slide") and name.endswith(".xml")]
        assert len(parts) == TOTAL
        ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
              "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
        for name in parts:
            root = ET.fromstring(archive.read(name))
            assert not root.findall(".//p:pic", ns)
            for shape in root.findall(".//p:sp", ns):
                if shape.find(".//a:custGeom", ns) is not None:
                    native_shapes += 1
                    assert shape.find("p:style", ns) is None
                if shape.find(".//a:t", ns) is not None:
                    text_boxes += 1
            assert all(el.attrib["val"] in ("000000", "FFFFFF")
                       for el in root.findall(".//a:srgbClr", ns))
    coverage = Counter(
        e["font"] for plate in plates for e in plate.elements if e["kind"] == "path"
    )
    assert sorted(coverage.values()) == [42, 42, 42, 42]
    result = {
        "slides": TOTAL, "blueprint_pages": 5, "outline_pages": 14,
        "standalone_glyph_svgs": 168, "raster_assets": 0,
        "native_powerpoint_vector_shapes": native_shapes,
        "editable_text_boxes": text_boxes, "checked_glyph_runs": path_count,
        "all_colors_black_or_white": True, "full_D1_text_preserved": True,
    }
    (OUT / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    check()
