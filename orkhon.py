#!/usr/bin/env python3
"""Transliterate modern Turkish text to Old Turkic (Orkhon) script.

Usage:
    python3 orkhon.py "Türkçe bir cümle yaz."
    echo "merhaba" | python3 orkhon.py          # reads stdin
    python3 orkhon.py --sep "⁚" "iki kelime"  # word divider char
    python3 orkhon.py --explain "dünya"        # show per-letter reasoning

Orkhon orthography notes:
- 4 vowel signs cover the 8 Turkish vowels: a/e, ı/i, o/u, ö/ü.
- Most consonants come in front/back pairs; the variant is chosen from
  the harmony class of the *adjacent* vowel (following vowel preferred).
- Some signs carry an inherent vowel (aq, ıq, oq...) which must match the
  adjacent real vowel, so e.g. back-k picks AQ/IQ/OQ by vowel quality.
- Cluster signs are used for lt, nt, nç, ny, and ŋ (written ng or ğ).
- Letters that didn't exist in Old Turkic are approximated:
  f/v -> p/b, h -> q, j -> y, c -> ç.
- The script is written right-to-left; Unicode bidi handles display.
"""

import sys
import unicodedata

# --- vowels -----------------------------------------------------------
VOWEL = {
    "a": "𐰀", "e": "𐰀",
    "ı": "𐰃", "i": "𐰃",
    "o": "𐰆", "u": "𐰆",
    "ö": "𐰇", "ü": "𐰇",
}
FRONT = set("eiöü")
BACK = set("aıou")

# --- consonants -------------------------------------------------------
# Single letters. "back"/"front" chosen by the reference vowel's harmony;
# "vowel" means the glyph is picked from the reference vowel's quality.
AB, AEB = "𐰉", "𐰋"          # b
AG, AEG = "𐰍", "𐰏"          # g
AD, AED = "𐰑", "𐰓"          # d
AY, AEY = "𐰖", "𐰘"          # y
AL, AEL = "𐰞", "𐰠"          # l
AN, AEN = "𐰣", "𐰤"          # n
AR, AER = "𐰺", "𐰼"          # r
AS, AES = "𐰽", "𐰾"          # s
AT, AET, OT = "𐱃", "𐱅", "𐱇"  # t
ASH, ESH = "𐰿", "𐱁"         # ş
AQ, IQ, OQ = "𐰴", "𐰶", "𐰸"  # q (back k / h)
AEK, OEK = "𐰚", "𐰜"         # k (front)
EP, OP = "𐰯", "𐰰"          # p
IC, EC = "𐰱", "𐰲"          # ç
EM, EZ = "𐰢", "𐰔"          # m, z (unpaired)
ENG, AENG = "𐰭", "𐰮"        # ŋ (ğ / ng)
# cluster signs
ELT, ENT, ENC, ENY = "𐰡", "𐰦", "𐰨", "𐰪"


def q_for(vowel):
    """Back-k/q glyph matching the neighbouring vowel."""
    if vowel in "a":
        return AQ
    if vowel == "ı":
        return IQ
    if vowel in "ou":
        return OQ
    # front context (harmony-breaking words): front-k instead
    return AEK if vowel in "ei" else OEK


def consonant(letter, ref):
    """Pick the Orkhon glyph for a consonant given its reference vowel."""
    front = ref in FRONT
    if letter == "b":
        return AEB if front else AB
    if letter == "v":
        return AEB if front else AB      # no v in Old Turkic -> b
    if letter == "g":
        return AEG if front else AG
    if letter == "ğ":
        return ENG                       # ğ -> ŋ (single Orkhon form; 𐰮 is Yenisei)
    if letter == "d":
        return AED if front else AD
    if letter == "j":
        return AEY if front else AY      # j -> y
    if letter == "y":
        return AEY if front else AY
    if letter == "l":
        return AEL if front else AL
    if letter == "n":
        return AEN if front else AN
    if letter == "r":
        return AER if front else AR
    if letter == "s":
        return AES if front else AS
    if letter == "ş":
        return ESH if front else ASH
    if letter == "t":
        return AET if front else (OT if ref in "ou" else AT)
    if letter == "k":
        return (AEK if ref in "ei" else OEK) if front else q_for(ref)
    if letter == "h":
        return q_for(ref)                # no h -> q
    if letter in "p":
        return EP if front else OP
    if letter == "f":
        return EP if front else OP       # f -> p
    if letter in "cç":
        return IC if ref in "iı" else EC # IC reads "ič/či"; EC is the general č
    if letter == "m":
        return EM
    if letter == "z":
        return EZ
    return None


CLUSTERS = {
    "lt": ELT, "nt": ENT, "nç": ENC, "ny": ENY,
    "ng": None,  # resolved as ŋ by harmony
}


def tr_lower(s):
    return s.replace("I", "ı").replace("İ", "i").lower()


def tokenize(word):
    """Split a word into ('v', char) / ('c', letter-or-cluster) tokens."""
    toks = []
    i = 0
    while i < len(word):
        ch = word[i]
        if ch in VOWEL:
            toks.append(("v", ch))
            i += 1
            continue
        pair = word[i:i + 2]
        if pair in CLUSTERS and all(c.isalpha() for c in pair):
            toks.append(("c", pair))
            i += 2
            continue
        toks.append(("c", ch))
        i += 1
    return toks


def ref_vowel(toks, idx):
    """Nearest vowel: prefer the next vowel, else the previous one."""
    for j in range(idx + 1, len(toks)):
        if toks[j][0] == "v":
            return toks[j][1]
    for j in range(idx - 1, -1, -1):
        if toks[j][0] == "v":
            return toks[j][1]
    return None


BASH = "𐱈"  # syllabic sign reading "baš"


def convert_word(word, explain=False):
    toks = tokenize(word)
    out, notes = [], []
    i = 0
    while i < len(toks):
        kind, t = toks[i]
        # the BASH glyph stands for the whole syllable "baş"
        if (t == "b" and i + 2 < len(toks)
                and toks[i + 1] == ("v", "a") and toks[i + 2][1] == "ş"
                and (i + 3 >= len(toks) or toks[i + 3][0] == "c")):
            out.append(BASH)
            notes.append("baş -> 𐱈 (BASH syllable sign)") if explain else None
            i += 3
            continue
        i += 1
        if kind == "v":
            out.append(VOWEL[t])
            notes.append(f"{t} -> {VOWEL[t]}") if explain else None
            continue
        if t in CLUSTERS:
            g = ENG if t == "ng" else CLUSTERS[t]
            out.append(g)
            notes.append(f"{t} -> {g} (cluster sign)") if explain else None
            continue
        ref = ref_vowel(toks, i - 1)
        g = consonant(t, ref or "e")
        if g is None:
            out.append(t)  # non-Turkic char passes through
            notes.append(f"{t} -> (unmapped)") if explain else None
        else:
            out.append(g)
            notes.append(f"{t} -> {g} (ref vowel {ref})") if explain else None
    return "".join(out), notes


def convert(text, sep=" "):
    words = text.split()
    rendered = []
    for w in words:
        # keep punctuation attached but outside the transliteration
        core = "".join(c for c in w if unicodedata.category(c).startswith("L"))
        trail = w[len(core):] if w.startswith(core) else w
        if not core:
            rendered.append(w)
            continue
        out, _ = convert_word(tr_lower(core))
        rendered.append(out + ("." if trail.startswith(".") else ""))
    return sep.join(rendered)


def main():
    args = sys.argv[1:]
    sep = " "
    explain = False
    if "--sep" in args:
        i = args.index("--sep")
        sep = args[i + 1]
        del args[i:i + 2]
    if "--explain" in args:
        explain = True
        args.remove("--explain")

    if args:
        text = " ".join(args)
    else:
        text = sys.stdin.read()

    if explain:
        for w in tr_lower(text).split():
            core = "".join(c for c in w if c.isalpha())
            if not core:
                continue
            out, notes = convert_word(core, explain=True)
            print(f"{core}:  {out}")
            for n in notes:
                print(f"    {n}")
    else:
        print(convert(tr_lower(text), sep))


if __name__ == "__main__":
    main()
