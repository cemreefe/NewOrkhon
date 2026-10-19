# New Orkhon / Yeni Orhun

**A proposed text hand, version 0.2.** Forty-two individually redrawn Orkhon
signs, compiled into an installable serif TrueType font. This is speculative
type design informed by script history, not a recovered historical stage or
an inevitable future for Orkhon.

## What history actually supports

There is no universal rule that old angles become modern curves. Latin
uncial rounded some capital forms; later Gothic writing introduced more
angular constructions. Renaissance humanists deliberately returned to
Caroline models. Early Greek minuscule developed from informal writing,
not by smoothing each majuscule outline. Cyrillic civil type was a deliberate
redesign involving new shapes and an alphabet reform.

Those are different mechanisms: a change of tool or writing practice,
standardization, selective revival, and explicit reform. Visual similarity
alone does not demonstrate a historical relationship between scripts.

The following names are **our design principles**, inferred from these
examples, not established historical laws.

## Seven tenets and their applications

### 1. Ductus over contour

**Evidence:** Latin uncial used round constructions particularly visible in
E, M and U; Greek minuscule grew from earlier informal/cursive practices.
[S1, S2]

**Inference:** Start from a plausible movement of the pen rather than preserve
every segment of an inscriptional outline.

**Application:** Back-b gets a returned neck and a bowl; back-d's two
zigzags become two serpentine strokes. A consistent contrast model and
bracketed stem terminals unify the font. These are new authored paths,
not skeletons extracted from Noto.

### 2. A shared vertical system

**Evidence:** Half-uncial developed ascenders and descenders. Caroline and
Greek minuscule use a four-line system rather than a uniform two-line
majuscule height. [S1, S2]

**Inference:** A text script can reorganize the vertical relationships of
letters, not merely change their edges.

**Application:** The first draft used a premature mixture of low bowls, tall
stems and descenders. It did not hold together. Revision 0.2 instead uses
a common 700-unit unicasal body on a zero baseline in a 1000-unit em,
with 10-unit optical overshoots on selected round edges. The plain fork
and trident are distinguished by their actual prongs, not arbitrary
different heights. Minuscule is a historical option, not a mandatory
destination for every modern script.

### 3. Reconstruction over tracing

**Evidence:** Greek majuscule and minuscule are substantially different
constructions; humanist Latin selectively revived Caroline writing rather
than preserving the immediately preceding Gothic forms. [S1, S2]

**Inference:** Letter identity need not mean one-to-one survival of corners,
strokes, or counters.

**Application:** The upper square of rounded-front-k opens into a shoulder;
its lower tier becomes an arch. This intentionally changes the old
enclosure. The square aš sign becomes an oval. Preserve a learnable
relationship, not an archaeological tracing.

### 4. Family grammar over isolated inventions

**Evidence:** Caroline was a clear, uniform book script assembled from
predecessor traditions. Cyrillic civil type deliberately regularized and
redesigned forms for printing. [S1, S3]

**Inference:** Repeated construction should be systematic across an alphabet.

**Application:** p and front-k share left-shoulder construction; l², č/i
and š share a fork vocabulary but differ in prongs and crossbar. The
n and ny bows share curvature but retain the ny notch. Family membership here
is a design proposal, not a claim that all paired signs were graphically
related historically.

### 5. Distinctness before economy

**Evidence:** Greek minuscule ligatures could share or omit strokes; scribes
also added extensions or spacing to avoid ambiguous readings. [S2]

**Inference:** Ease of production is constrained by the distinctions readers
need. Simplification is not always progress.

**Application:** Keep the three dots in nt, the second shoulder of r²,
the š crossbar and the ny notch. Do not merge the two b signs or the two
n signs merely to reduce the inventory. Front/back pairs still have
different identities.

### 6. Optical rhythm over equal boxes

**Evidence:** Modern type design uses overshoot for round and pointed
forms. Fernando Mello, drawing on Tracy, Smeijers and Kindersley, explains
why inner and outer white space must be balanced and why equal numerical
gaps do not produce equal perceived space. These are typographic engineering
precedents, not palaeographic laws. [S4, S6]

**Inference:** A coherent alphabet requires unequal measurements in some
places, not identical boxes.

**Application:** Selected round forms reach 710/-10 against a 700/0 body.
The oval and closed bowls establish related counter proportions. Side spaces
are assigned by the shape of each edge: stem, round, diagonal or open,
then examined in repeated and mixed strings. They are not identical margins
or monospaced boxes. The 64-unit vertical and 30-unit horizontal stroke
envelopes are continuous, united geometrically at joins, and fitted before
the font advances are calculated. Stem serifs are bracketed, not added to
every arbitrary endpoint. The double-roof stem ends at its valley.

This spacing system is a starting fit plus visual review, not an automatic
formula claiming to solve optical balance.

### 7. Separate typeface reform from alphabet reform

**Evidence:** Cyrillic civil reform changed both forms and inventory.
These are separable decisions, not one inseparable operation. [S3]

**Application:** Change outlines only. Keep the existing Orkhon Unicode
characters and right-to-left order. Do not silently invent distinct modern
Turkish vowel letters or signs for f/v/c/j/h. The font does not fix or
translate an orthography. Such changes require a separate proposal.

## Reading the specimens

Gray references are **Noto Sans Old Turkic**, a modern reference font, not
facsimiles of inscriptions. Black forms are New Orkhon. Both represent the
same encoded signs. Comparison sheets proceed left to right for convenience;
actual Orkhon words run right to left.

The text sheet uses illustrative modern Turkish transliterations with vowels
written out. It does not reproduce historical spelling. Words were chosen
to avoid the unsupported modern consonants; no claim of reversible
transliteration is made. The earlier converter is not an authority for the
historical orthography.

## What is not proved

- No reader study or handwriting-speed trial has established better
  readability, learnability or fewer pen lifts. Those remain hypotheses.
- This is not a production family: no hinting, kerning, italic, bold,
  contextual alternates, or separate optical sizes yet.
- The font covers 42 Unicode signs explicitly named ORKHON, not the full
  Old Turkic block or Yenisei variants. It also contains space, full stop,
  comma and the two-dot divider U+205A.
- Font loading, coverage, common vertical zones, the non-protruding roof join,
  fork/trident identity, three-dot separation, outline bounds and RTL raster
  order are checked automatically; that does not establish linguistic validity.

## Sources

**S1 — University of Zurich, Ad fontes: history of Latin scripts.**
Sections: Uncial and Half-Uncial; Insular Scripts; Caroline Minuscule;
Humanist Minuscule and Cursives. Also documents the adoption of runic
wynn and thorn into manuscript writing: an actual rune-to-book-script
precedent, but not proof of an Orkhon genealogy.
https://www.adfontes.uzh.ch/en/tutorium/schriften-lesen/schriftgeschichte/humanistische-minuskel-und-kursive/

**S2 — Timothy Janz / Vatican Library: Introduction to Minuscule Bookhands.**
Quadrilinear organization, development from informal writing, ligatures
and deliberate disambiguation.
https://spotlight.vatlib.it/en/greek-paleography/feature/2-introduction-to-minuscule-bookhands

**S3 — Presidential Library: Peter the Great approved the new alphabet.**
1708 printing and 1710 final approval; simultaneous redesign of forms
and alphabet composition. Its claim of simpler/rounder forms describes
this particular reform, not all script evolution.
https://www.prlib.ru/en/history/619018

**S4 — Ralf Herrmann, Typography.Guru: Overshoot.**
https://typography.guru/term/overshoot-r82/

**S5 — Unicode Consortium: Old Turkic code chart.**
Encoding and reference glyph labels; this is not an orthographic handbook.
https://www.unicode.org/charts/PDF/U10C00.pdf

**S6 — Fernando Mello: How to space a typeface.**
Optical centre; counterspace versus inter-letter space; straight, round
and mixed controls. Directly informed the 0.2 spacing revision.
https://www.myfonts.com/a/font/content/how-to-space-a-typeface

**S7 — Society of Fonts: Spacing a Font, Part 1.**
Practical account of the Tracy method. Distinguishes basic fitting from
pair kerning; explains repeated upright/round control strings.
https://www.societyoffonts.com/2018/09/19/spacing-a-font-part-1/

**S8 — Anton Koovit: U8.**
A designer's account of turning inconsistent historical station lettering
into a text face and checking weight at the intended physical size.
This informed the proofing method, not a claim that U8 and Orkhon
are historically related.
https://www.antonkoovit.com/typefaces/u8

**Reference font and license:** Noto Sans Old Turkic (Google), SIL Open Font
License 1.1. New Orkhon's paths were authored independently by visual
reference; Noto's outlines are not used by the build. The license and both
copyright notices are included with the source package.
https://github.com/notofonts/old-turkic

## Build and inspect

```sh
python3 -m pip install -r requirements.txt
python3 build.py
python3 specimen.py
python3 validate.py
python3 report.py
```

Pillow must have libraqm support for correct RTL rendering. Strings are
stored in logical order, passed with `direction="rtl"`, and never reversed
by hand. The renderer tests that the initial t² in Türk lands at the
right edge.
