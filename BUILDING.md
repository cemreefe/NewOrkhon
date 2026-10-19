# New Orkhon / Yeni Orhun

Orkhon script reimagined for a modern era.

This package contains the original Serif and its neutral Sans companion, release
0.16.2. Each covers 42 encoded Orkhon signs, with 42 capitals and 42 lowercase forms.
It is speculative type design, not a recovered historical stage.

## Deliverables

- `output/New-Orkhon.pdf`: 14-slide black-and-white presentation. The complete
  Kül Tigin D1 passage comes first in Serif and Sans, followed by construction.
- `output/New-Orkhon.pptx`: editable PowerPoint. Latin labels are native text;
  Orkhon letters are native editable vector paths, not screenshots.
- `output/New-Orkhon-Blueprints.pdf`: five construction and measurement plates.
- `output/New-Orkhon-Outlines.pdf`: 14 pages covering all 168 standalone forms
  across both families.
- `output/glyph-outlines/{serif,sans}/`: 84 individual contour SVGs per family.
- `output/slide-*.svg`, `output/outline-plate-*.svg`, `output/slides.json`:
  exact vector artwork and scene source.
- `typeface/New-Orkhon-Showcase.html`: offline text specimen, with Serif/Sans,
  case, size and spacing controls.
- `word-comparison/New-Orkhon-Sans-Case-Comparison.{png,pdf,svg}`: ten sourced words
  in original Orkhon, Sans lowercase and Sans uppercase, with Latin readings and Turkish glosses.
  The PNG is 2600 × 3280 pixels; the PDF and SVG contain vector outlines.

## Install the typefaces

Install either or both defaults in `typeface/`:

| Typeface | Default capitals | Default lowercase |
|---|---|---|
| Serif | `NewOrkhonText-Regular.ttf` | `NewOrkhonTextLowercase-Regular.ttf` |
| Sans | `NewOrkhonSans-Regular.ttf` | `NewOrkhonSansLowercase-Regular.ttf` |

The capital-default fonts use `ss01` for lowercase; lowercase-default fonts use
`ss02` for capitals. They use the original Old Turkic Unicode characters and
logical RTL text. Do not reverse strings manually. `kern` enables safe AL fitting;
`liga` enables matching-case EM–I joins. The text remains two Unicode characters.

For PowerPoint text editing, install the Instrument Sans and JetBrains Mono
fonts supplied in `assets/`. All Orkhon artwork remains visible as vectors without
installing the Orkhon fonts. Replace or regenerate that artwork from the
logical Unicode in `slides.json` or `deck.py`; it is not live text in the slides.

## Rebuild

Python 3.11 or newer is recommended. Pillow needs libraqm for the proof and
shaping checks. Debian/Ubuntu proof labels use `fonts-dejavu-core`.

```sh
python3 -m pip install -r requirements.txt
python3 typeface/build.py
python3 typeface/validate.py
python3 typeface/construction_revision.py
python3 typeface/validate_sans.py
python3 typeface/shaping_revision.py
python3 typeface/fit_revision.py
python3 typeface/bash_spacing.py
python3 typeface/em_alpha_study.py
python3 typeface/showcase.py --update
python3 deck.py
python3 audit_deck.py
python3 compare_words.py
```

The four TTFs have deterministic timestamps and rebuild byte-for-byte.
The slide PDF and all SVG artwork are rendered as vectors. PowerPoint was also
rendered through LibreOffice to check its native geometry and text layout.
Exact editable text metrics can vary slightly between presentation applications.

`typeface/DESIGN.md` contains design decisions and historical sources.
`typeface/analysis/` contains focused before/after proofs and validation results.
The AD/ENC paired-return study is **not applied** to either family.
Sans 0.16 fits the writing routes before outlining, without the blanket
cap/body/baseline crop used in 0.15. Pen weights and deliberate round overshoots
are retained. IC has genuine flat middle terminals rather than a trimmed bump;
OE's curved shoulder and upright post are independently constructed.
The capital AG's detached staff extends upward without joining its horns.
ENC's bowl routes are inset by half the local thin stroke so their outer curves
meet the cap/body line and baseline without a chopped corner.
Serif A's internal corner feet now follow the diagonal rather than using the
upright fallback. Other Serif outlines remain unchanged from 0.15.
BASH's 0.16.1 placement change is reverted in 0.16.2. All glyph outlines,
metrics and OpenType shaping tables match 0.16 again; `bash_spacing.py` checks this.
The mirrored-alpha EM study is **not applied**. Its revised Serif design has
two serifed open ends and no descender; it is included as a comparison only.

## Licenses and attribution

- New Orkhon and Noto Sans Old Turkic: SIL OFL 1.1; see `typeface/OFL.txt`.
- Instrument Sans: SIL OFL 1.1; see `assets/InstrumentSans-OFL.txt`.
- The bundled JetBrains Mono version: Apache 2.0; see its copyright and
  full license in `assets/`.
- Kül Tigin transcription and Turkish translation: Turkish Wikisource
  contributors, [Orhun Yazıtları (Kül Tigin)](https://tr.wikisource.org/wiki/Orhun_Yaz%C4%B1tlar%C4%B1_(K%C3%BCl_Tigin)),
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
  Adaptations: normalized word spaces, the documented Orkhon EZ substitution,
  editorial case and typeset line breaks. The adapted text presentation is
  shared under the same license; fonts retain their separate licenses.

Helvetica is a design reference for optical balance and neutral grotesk
construction. No Helvetica font files or outlines are included or used.
Outline and shaping checks do not establish reader performance.
