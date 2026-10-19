"""Verify that the BASH revert restores all four fonts to 0.16 geometry."""

import json

from fontTools.ttLib import TTFont

from build import ROOT, VERSION
from shaping_revision import shaped

BASE = ROOT / "archive-v016"
TARGETS = {"u10C48", "u10C48.lc"}
PROBES = ("𐰃𐱈𐰃", "𐰞𐱈", "𐱈𐰢𐱈")


def checks() -> None:
    records = []
    for style in ("Text", "Sans"):
        for default in ("", "Lowercase"):
            filename = f"NewOrkhon{style}{default}-Regular.ttf"
            old, new = TTFont(BASE / filename), TTFont(ROOT / filename)
            assert old.getBestCmap() == new.getBestCmap()
            assert old.getGlyphOrder() == new.getGlyphOrder()
            for name in old.getGlyphOrder():
                before, after = old["glyf"][name], new["glyf"][name]
                assert before.compile(old["glyf"]) == after.compile(new["glyf"]), name
                assert old["hmtx"][name] == new["hmtx"][name], name
                if name in TARGETS:
                    advance = new["hmtx"][name][0]
                    records.append({
                        "font": filename, "glyph": name, "shift_from_016": 0,
                        "advance": advance, "left": after.xMin,
                        "right": advance - after.xMax,
                    })
            for tag in ("GSUB", "GPOS", "GDEF"):
                assert old[tag].compile(old) == new[tag].compile(new), (filename, tag)
            for probe in PROBES:
                for features in ({}, {"kern": 0}, {"ss01": 1}, {"ss02": 1}):
                    assert shaped(BASE / filename, probe, features) == shaped(
                        ROOT / filename, probe, features,
                    )
    (ROOT / "analysis" / "bash-spacing-checks.json").write_text(json.dumps({
        "version": VERSION, "base": "0.16", "bash_shift_reverted": True,
        "all_outlines_metrics_and_shaping_match_base": True,
        "measurements": records,
    }, indent=2) + "\n")
    print("PASS: all outlines, metrics, GSUB, GPOS and GDEF match 0.16 in all 4 fonts.")


if __name__ == "__main__":
    checks()
