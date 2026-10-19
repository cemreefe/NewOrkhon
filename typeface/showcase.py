"""Build the offline showcase body for the Devin artifact compiler."""

import base64
import html
import json
import re
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

from build import VERSION

ROOT = Path(__file__).resolve().parent
WIKI = "https://tr.wikisource.org/wiki/Orhun_Yaz%C4%B1tlar%C4%B1_(K%C3%BCl_Tigin)"
BITIG = "https://bitig.kz/?lang=e&m=1&mod=1&oid=15&tid=1"
import sys as _sys  # noqa: E402

_sys.path.insert(0, str(ROOT.parent))
from orkhon import convert_word, tr_lower  # noqa: E402

ROWS = json.loads((ROOT / "wikisource-rows.json").read_text(encoding="utf-8"))
NAMES = {"türk", "bumın", "istemi", "teŋri", "ötüken", "tokuz", "oguz", "tabgaç",
         "kadırkan", "temir", "kapıgka", "tatar", "şadpıt", "tarkat"}
FACES = {"G": "South face", "D": "East face"}
TITLES = {
    "D1": "The sky, the earth and the first kağans",
    "D2": "Four quarters of the world",
    "D3": "Wise kağans and an orderly people",
    "G1": "Bilge Kağan addresses his people",
    "G2": "To the Nine Oğuz, in all directions",
}
MODERN = [
    ("Ankara and İstanbul",
     "Ayşe Ankara yolunda. Mehmet İstanbul şehrinde kaldı. Akşam Konya ile Bursa arasında buluşacaklar."),
    ("A short letter",
     "Sevgili Deniz. Yarın Orhan Bey ile Ötüken kitabını okuyacağız. Sen de gel. Kemal ve Elif bizi bekliyor."),
    ("About this typeface",
     "Yeni Orhun bir deneme yazısıdır. Büyük harf cümle başında ve özel adlarda kullanılır. Küçük harf metni sakinleştirir."),
]


def clean_words(text):
    return [word.strip() for word in re.split(r":\s*", text) if word.strip()]


def historical(key):
    _, _, raw, _, latin, turkish = ROWS[key]
    words = clean_words(raw)
    latin_words = [tr_lower(word).replace("ŋ", "ŋ") for word in clean_words(latin)]
    assert len(words) == len(latin_words), key
    caps = {0}
    for number, word in enumerate(latin_words):
        if word in NAMES or (word == "kök" and number + 1 < len(latin_words)
                             and latin_words[number + 1] == "türk"):
            caps.add(number)
        if re.search(r"(m[ıiuü]ş|t[ıi]m|gil)$", word) and number + 1 < len(latin_words):
            caps.add(number + 1)
    reading = " ".join(word[:1].upper().replace("I", "İ") + word[1:] if i in caps and word[:1] == "i"
                       else (word[:1].upper() + word[1:] if i in caps else word)
                       for i, word in enumerate(latin_words))
    return {
        "kind": "historical", "key": key, "title": TITLES[key],
        "location": f"{key} · {FACES[key[0]]}, line {key[1:]} · complete line",
        "raw": raw, "words": [word.replace("𐰕", "𐰔") for word in words],
        "separator": " ⁚ ", "reading": reading, "translation": turkish,
        "caps": sorted(caps),
    }


def modern(title, text):
    words, caps = [], []
    for number, token in enumerate(text.split()):
        core = "".join(char for char in token if char.isalpha())
        glyphs, _ = convert_word(tr_lower(core))
        words.append(glyphs + ("." if token.endswith(".") else ""))
        if core[:1].isupper():
            caps.append(number)
    return {
        "kind": "modern", "title": title, "location": "Modern Turkish · illustrative transliteration",
        "words": words, "separator": " ", "reading": text,
        "translation": "Not historical Old Turkic: generated with orkhon.py, all vowels written.",
        "caps": caps,
    }


PASSAGES = [historical(key) for key in ("D1", "D2", "D3", "G1", "G2")] + [
    modern(title, text) for title, text in MODERN]


def esc(value):
    return html.escape(str(value), quote=True)


def face(family, filename):
    encoded = base64.b64encode((ROOT / filename).read_bytes()).decode("ascii")
    return (
        "@font-face{font-family:'"
        + family
        + "';src:url(data:font/ttf;base64,"
        + encoded
        + ") format('truetype');font-weight:400;font-style:normal;font-display:block}"
    )


def passage_markup(index, passage):
    words = passage["words"]
    separator = passage["separator"]
    text = separator.join(words)
    cmap = TTFont(ROOT / "NewOrkhonText-Regular.ttf").getBestCmap()
    assert all(ord(char) in cmap or char in "[]" for word in words for char in word), passage["title"]

    def capitalized(word):
        start = next(i for i, char in enumerate(word) if ord(char) in cmap and char != ".")
        return f'{word[:start]}<span class="initial">{word[start]}</span>{word[start + 1:]}'

    mixed = separator.join(
        '<span class="word">'
        + (capitalized(word) if number in passage["caps"] else word)
        + "</span>"
        for number, word in enumerate(words)
    )
    historical = passage["kind"] == "historical"
    eyebrow = ("Kül Tigin · 732 CE · " if historical else "") + passage["location"]
    reading_label = "Latin reading" if historical else "Turkish source text"
    translation_label = "Türkiye Türkçesi" if historical else "Note"
    if historical:
        source = f"""<details class="source a-no-print">
    <summary>Source and transcription</summary>
    <p><a href="{WIKI}" target="_blank" rel="noopener">Wikisource · {esc(passage["key"])}</a>.
    The exact source string is below. YENISEI EZ (U+10C15) is shown as ORKHON EZ (U+10C14),
    the counterpart covered by this typeface. Colons are shown as ⁚ dividers;
    square brackets mark the edition’s restored text.
    Screen line breaks are not inscription lines.</p>
    <p class="raw-source traditional" lang="otk" dir="rtl">{esc(passage["raw"])}</p>
    <p>Capitals mark the line start, names and the word after each finite verb ending
    (-mIş, -tIm, -gil): an approximate editorial rule, not part of the inscription.
    The Latin reading follows the Wikisource transcription; the translation is Wikisource's.</p>
  </details>
  <p class="print-source">Source: Wikisource, Orhun Yazıtları (Kül Tigin), {esc(passage["key"])}.</p>"""
    else:
        source = ""
    return f"""
<article class="passage a-section" data-passage="{index}">
  <header class="passage-heading">
    <div>
      <p class="eyebrow">{esc(eyebrow)}</p>
      <h2>{esc(passage["title"])}</h2>
    </div>
    <span class="direction">Read right to left ←</span>
  </header>
  <div class="comparison">
    <section class="specimen original-pane" aria-labelledby="original-{index}">
      <h3 id="original-{index}"><span>01</span> Traditional forms</h3>
      <p class="runic traditional" lang="otk" dir="rtl">{text}</p>
      <p class="specimen-note">Noto Sans Old Turkic · digital transcription</p>
    </section>
    <section class="specimen new-pane" aria-labelledby="new-{index}">
      <h3 id="new-{index}"><span>02</span> New Orkhon <small class="style-name">Serif</small><small class="case-name">Mixed case</small></h3>
      <p class="runic new-case" lang="otk" dir="rtl">{mixed}</p>
      <p class="specimen-note">New Orkhon <span class="style-name">Serif</span> {VERSION} · same sign sequence · {len(passage["caps"])} capitals</p>
    </section>
  </div>
  <div class="readings">
    <section>
      <h3>{reading_label}</h3>
      <p lang="{"otk-Latn" if historical else "tr"}">{esc(passage["reading"])}</p>
    </section>
    <section>
      <h3>{translation_label}</h3>
      <p lang="{"tr" if historical else "en"}">{esc(passage["translation"])}</p>
    </section>
  </div>
  {source}
</article>"""


CSS = """
<style>
:root { --specimen-size: 52px; --max-width: 1280px; }
.a-shell { padding-top: 28px; }
.a-header { padding-bottom: 20px; margin-bottom: 0; }
.a-header__title { font-size: clamp(32px, 5vw, 56px); letter-spacing: -.04em; line-height: 1; }
.a-header__subtitle { margin-top: 10px; }
.a-header__title::after { content: " / Yeni Orhun"; font-size: .43em; font-weight: 400; letter-spacing: -.02em; color: rgb(var(--text-secondary)); }
.edition { display: block; font: 11px var(--font-mono); letter-spacing: .06em; color: rgb(var(--text-secondary)); margin-bottom: 10px; }
.toolbar { border-block: 1px solid rgb(var(--border-primary)); display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 1.4fr; gap: 24px; padding: 14px 0; margin-bottom: 24px; align-items: end; }
.control-label { display: block; font-size: 11px; letter-spacing: .07em; text-transform: uppercase; color: rgb(var(--text-secondary)); margin-bottom: 6px; }
.navigation { display: flex; gap: 8px; align-items: center; }
.navigation output { min-width: 45px; text-align: center; font: 13px var(--font-mono); }
.navigation button { min-width: 44px; min-height: 36px; }
.toolbar select { width: 100%; min-height: 36px; background: rgb(var(--bg-page)); color: rgb(var(--text-primary)); border: 1px solid rgb(var(--border-primary)); border-radius: 4px; padding: 4px 8px; font: inherit; }
.size-control { display: flex; align-items: center; gap: 10px; min-height: 36px; }
input[type=range] { width: 100%; min-width: 0; accent-color: rgb(var(--text-primary)); }
.size-control output { min-width: 38px; font: 12px var(--font-mono); white-space: nowrap; }
.passage-heading { display: flex; justify-content: space-between; gap: 12px; align-items: end; margin-bottom: 20px; }
.eyebrow { font: 11px var(--font-mono); color: rgb(var(--text-secondary)); margin: 0 0 7px; }
.passage-heading h2 { font-size: 23px; letter-spacing: -.02em; line-height: 1.25; margin: 0; font-weight: 500; }
.direction { font-size: 11px; white-space: nowrap; color: rgb(var(--text-secondary)); padding-bottom: 3px; }
.comparison { display: grid; grid-template-columns: 1fr 1fr; border: 1px solid rgb(var(--border-primary)); }
.specimen { min-width: 0; padding: 20px 24px 12px; display: flex; flex-direction: column; }
.specimen + .specimen { border-left: 1px solid rgb(var(--border-primary)); }
.specimen h3 { font-size: 12px; font-weight: 500; margin: 0 0 18px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.specimen h3 > span { color: rgb(var(--text-secondary)); font: 10px var(--font-mono); }
.specimen h3 small { color: rgb(var(--text-secondary)); font-size: 11px; margin-left: auto; font-weight: 400; }
.traditional { font-family: OrkhonReference, NewUpper, serif; }
.new-case { font-family: NewUpper, serif; font-feature-settings: "ss01" 1; font-kerning: normal; font-variant-ligatures: common-ligatures; }
:root[data-style=sans] .new-case { font-family: NewSans, sans-serif; }
[data-spacing=off] .new-case { font-kerning: none; font-variant-ligatures: none; }
.layout-control { display: flex; align-items: center; gap: 7px; margin: -10px 0 18px; font-size: 12px; }
:root:not([data-case]) .new-case .initial, [data-case=mixed] .new-case .initial { font-feature-settings: "ss01" 0; }
[data-case=uppercase] .new-case, [data-case=uppercase] .new-case .initial { font-feature-settings: "ss01" 0; }
.runic { font-size: var(--specimen-size); line-height: 1.7; font-weight: 400; font-synthesis: none; letter-spacing: 0; text-align: right; unicode-bidi: isolate; margin: 0; padding-block: .15em .3em; overflow-wrap: anywhere; flex-grow: 1; }
.specimen-note { font: 10px var(--font-mono); color: rgb(var(--text-secondary)); margin: 16px 0 0; }
.readings { display: grid; grid-template-columns: 1fr 1fr; gap: 36px; margin-top: 20px; }
.readings h3 { font-size: 10px; text-transform: uppercase; letter-spacing: .07em; font-weight: 500; color: rgb(var(--text-secondary)); margin: 0 0 7px; }
.readings p { font-size: 16px; line-height: 1.55; margin: 0; }
.readings section:first-child p { font-family: Georgia, serif; font-style: italic; font-size: 19px; }
.source { margin-top: 18px; }
details summary { cursor: pointer; font-size: 12px; }
details > p { font-size: 13px; line-height: 1.65; max-width: 900px; }
.raw-source { font-size: 30px; overflow-wrap: anywhere; border-top: 1px solid rgb(var(--border-primary)); padding-top: 12px; }
.about { margin-top: 24px; padding-top: 18px; border-top: 1px solid rgb(var(--border-primary)); }
.about details { margin-top: 14px; }
.about h3 { font-size: 13px; margin: 18px 0 4px; }
.about p { font-size: 13px; line-height: 1.6; max-width: 900px; }
.about pre { white-space: pre-wrap; font-size: 11px; line-height: 1.6; max-height: 340px; overflow: auto; }
.print-source { display: none; }
.a-footnote { font-size: 11px; line-height: 1.6; margin-top: 16px; }
[data-view=traditional] .new-pane, [data-view=new] .original-pane { display: none; }
[data-view=traditional] .comparison, [data-view=new] .comparison { grid-template-columns: 1fr; }
[data-view=new] .new-pane { border-left: 0; }
@media (max-width: 680px) {
  :root { --specimen-size: 28px; }
  .a-shell { padding: 18px 16px; }
  .a-header { padding-bottom: 12px; gap: 8px; }
  .a-header__title { font-size: 32px; }
  .a-header__subtitle { display: none; }
  .edition { font-size: 10px; }
  .toolbar { grid-template-columns: 1fr 1fr; gap: 8px 18px; padding: 10px 0; margin-bottom: 18px; }
  .passage.a-section { margin-block: 0; }
  .control-label { font-size: 10px; margin-bottom: 3px; }
  .navigation button, .toolbar select { min-height: 36px; }
  .passage-heading { margin-bottom: 12px; }
  .passage-heading h2 { font-size: 19px; }
  .eyebrow { font-size: 9px; }
  .direction { display: none; }
  .comparison, .readings { grid-template-columns: 1fr; }
  .specimen { padding: 14px 16px 10px; }
  .specimen + .specimen { border-left: 0; border-top: 1px solid rgb(var(--border-primary)); }
  [data-view=new] .new-pane { border-top: 0; }
  .specimen h3 { margin-bottom: 8px; }
  .runic { line-height: 1.5; }
  .specimen-note { font-size: 8px; margin-top: 8px; }
  .readings { gap: 12px; margin-top: 16px; }
  .readings h3 { margin-bottom: 4px; }
  .readings p { font-size: 14px; line-height: 1.45; }
  .readings section:first-child p { font-size: 16px; }
  .source { margin-top: 14px; }
  .about { margin-top: 8px; padding-top: 8px; }
  .a-footnote { font-size: 10px; margin-top: 10px; }
}
@media print {
  :root { --specimen-size: 26px !important; }
  .a-shell { padding: 0; }
  .a-header { margin-bottom: 20px; }
  .passage, .passage[hidden] { display: block !important; break-inside: avoid; break-after: page; }
  .passage:last-of-type { break-after: auto; }
  .comparison { grid-template-columns: 1fr 1fr !important; }
  .specimen { display: flex !important; padding: 14px; border-top: 0; }
  .specimen + .specimen { border-left: 1px solid #bbb !important; }
  .readings { grid-template-columns: 1fr 1fr; }
  .print-source { display: block; font-size: 9px; margin-top: 12px; }
  .a-footnote { font-size: 9px; }
}
</style>
"""

CONTROLS = """
<div class="toolbar a-no-print" aria-label="Specimen controls">
  <div>
    <span class="control-label">Passage</span>
    <div class="navigation">
      <button class="a-btn" id="previous" type="button" aria-label="Previous passage">←</button>
      <output id="position" aria-live="polite" aria-atomic="true">1 / 8</output>
      <button class="a-btn" id="next" type="button" aria-label="Next passage">→</button>
    </div>
  </div>
  <label>
    <span class="control-label">View</span>
    <select id="view">
      <option value="both">Compare both</option>
      <option value="traditional">Traditional forms</option>
      <option value="new">New Orkhon</option>
    </select>
  </label>
  <label>
    <span class="control-label">New Orkhon case</span>
    <select id="case">
      <option value="mixed">Mixed case</option>
      <option value="lowercase">Lowercase</option>
      <option value="uppercase">Capitals</option>
    </select>
  </label>
  <label>
    <span class="control-label">Typeface</span>
    <select id="style">
      <option value="serif">Serif</option>
      <option value="sans">Sans</option>
    </select>
  </label>
  <label>
    <span class="control-label">Text size</span>
    <span class="size-control">
      <input type="range" id="size" min="24" max="84" value="52" step="2">
      <output id="size-value" for="size">52 px</output>
    </span>
  </label>
</div>
<label class="layout-control a-no-print"><input type="checkbox" id="spacing" checked> Spacing and joins</label>
<noscript><p>JavaScript is off: all passages are shown below. The fonts still work.</p></noscript>
"""

SCRIPT = """
<script>
(() => {
  "use strict";
  const root = document.documentElement;
  const passages = [...document.querySelectorAll(".passage")];
  const previous = document.getElementById("previous");
  const next = document.getElementById("next");
  const view = document.getElementById("view");
  const letterCase = document.getElementById("case");
  const fontStyle = document.getElementById("style");
  const size = document.getElementById("size");
  let current = 0;
  function show(index) {
    current = Math.max(0, Math.min(passages.length - 1, index));
    passages.forEach((passage, number) => { passage.hidden = number !== current; });
    previous.disabled = current === 0;
    next.disabled = current === passages.length - 1;
    document.getElementById("position").textContent = `${current + 1} / ${passages.length}`;
  }
  function setView() { root.dataset.view = view.value; }
  function setStyle() {
    root.dataset.style = fontStyle.value;
    document.querySelectorAll(".style-name").forEach(label => {
      label.textContent = fontStyle.options[fontStyle.selectedIndex].text;
    });
  }
  function setCase() {
    root.dataset.case = letterCase.value;
    document.querySelectorAll(".case-name").forEach(label => {
      label.textContent = letterCase.options[letterCase.selectedIndex].text;
    });
  }
  function setSize() {
    root.style.setProperty("--specimen-size", `${size.value}px`);
    document.getElementById("size-value").textContent = `${size.value} px`;
  }
  previous.addEventListener("click", () => show(current - 1));
  next.addEventListener("click", () => show(current + 1));
  view.addEventListener("change", setView);
  letterCase.addEventListener("change", setCase);
  fontStyle.addEventListener("change", setStyle);
  size.addEventListener("input", setSize);
  const spacing = document.getElementById("spacing");
  spacing.addEventListener("change", () => {
    root.dataset.spacing = spacing.checked ? "on" : "off";
  });
  if (matchMedia("(max-width: 680px)").matches) {
    view.value = "new";
    size.value = "28";
  }
  show(0);
  setView();
  setCase();
  setStyle();
  setSize();
  Promise.all([
    document.fonts.load('36px "OrkhonReference"', "𐰇𐰔𐰀"),
    document.fonts.load('36px "NewUpper"', "𐰇𐰔𐰀"),
    document.fonts.load('36px "NewSans"', "𐰇𐰔𐰀")
  ]).then(fonts => {
    if (fonts.some(list => list.length === 0)) throw new Error("An embedded font did not load.");
    root.dataset.fontsReady = "true";
  }).catch(error => {
    const alert = document.querySelector("[data-a-error]");
    alert.hidden = false;
    document.querySelector("[data-a-error-detail]").textContent = error.message;
  });
})();
</script>
"""


def main():
    font_css = "<style>" + face(
        "OrkhonReference", "NotoSansOldTurkic-Regular.ttf"
    ) + face("NewUpper", "NewOrkhonText-Regular.ttf") \
        + face("NewSans", "NewOrkhonSans-Regular.ttf") + "</style>"
    licenses = esc((ROOT / "OFL.txt").read_text())
    about = f"""
<details class="about a-no-print">
  <summary>About New Orkhon · sources and license</summary>
  <h3>Typography, not a rewritten alphabet</h3>
  <p>Both main views use the same logical RTL text, including the inscription’s
  unwritten vowels. Only the letterforms change. New Orkhon’s capitals and
  lowercase are alternate glyphs, not Unicode case pairs. Mixed case capitalizes
  line starts, names and approximate sentence starts in the five complete
  Kül Tigin lines, and Latin capitals in the three modern samples. These choices
  are editorial, not features of the historical inscription. Modern samples
  are illustrative transliterations, not Old Turkic.</p>
  <p>In the font, OpenType <code>ss01</code> selects lowercase; disabling it selects
  capitals. The original script has no such case distinction.</p>
  <h3>Reference and limits</h3>
  <p>The reference is Noto Sans Old Turkic, not a facsimile or a claim about the
  exact shapes on the stone. Source Unicode strings are available under each
  passage. D1’s EZ variant and the display of word dividers are documented there.
  New Orkhon is speculative authored typography; reader performance and historical
  or linguistic validity have not been established.</p>
  <p>Transcription attribution:
  <a href="{WIKI}" target="_blank" rel="noopener">Turkish Wikisource contributors,
  Orhun Yazıtları (Kül Tigin)</a>,
  <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>.
  The adapted text presentation is shared under that license; fonts retain their
  separate SIL OFL license.
  D1 reading cross-check:
  <a href="{BITIG}" target="_blank" rel="noopener">Turk Bitig · Kultegin, line 1</a>.
  Readings use ŋ for /ŋ/; translation choices vary between editions.</p>
  <h3>Embedded font licenses</h3>
  <p>Noto font metadata: Copyright 2017–2022 Google Inc. All Rights Reserved.
  New Orkhon Text: Copyright 2026 New Orkhon contributors.</p>
  <details><summary>SIL Open Font License 1.1 · full text</summary><pre>{licenses}</pre></details>
  <p>The reference, Serif and Sans fonts are embedded. This file needs no server or internet connection.</p>
</details>"""
    body = "<!-- NEW-ORKHON-BODY:START -->\n" + (
        font_css + CSS + CONTROLS
        + "".join(passage_markup(i, p) for i, p in enumerate(PASSAGES))
        + about + SCRIPT
    ) + "\n<!-- NEW-ORKHON-BODY:END -->"
    (ROOT / "showcase-body.html").write_text(body, encoding="utf-8")
    (ROOT / "showcase-sources.json").write_text(
        json.dumps({"source": WIKI, "cross_check": BITIG, "passages": PASSAGES},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if "--update" in sys.argv:
        output = ROOT / "New-Orkhon-Showcase.html"
        document = output.read_text(encoding="utf-8")
        document, count = re.subn(
            r"<!-- NEW-ORKHON-BODY:START -->.*?<!-- NEW-ORKHON-BODY:END -->",
            lambda _: body, document, flags=re.DOTALL,
        )
        if count != 1:
            raise ValueError("Compile the fragment into the artifact shell once before updating.")
        output.write_text(document, encoding="utf-8")
    print("Wrote showcase-body.html; all passage signs covered by the current font.")


if __name__ == "__main__":
    main()
