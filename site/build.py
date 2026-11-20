"""Builds Javni uvid's own page (site/index.html) in both scripts, with the family's look from shared/design/.

The page is written once, in Cyrillic, and turned into Latin letter by letter (the other way is ambiguous:
"nj" is њ in "konj" and нј in "injekcija"). The Latin page is the default, the Cyrillic one is under cir/, as on
the family's other sites. The build fails when a page loads anything from another server (principle 5), keeps a
Cyrillic letter on the Latin page, or leaves a site of sites.json out.

    uv run --no-project site/build.py --out _site
"""

import argparse
import datetime
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESIGN = HERE.parent / "shared" / "design"

MARK = (
    '<svg class="ju-mark" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="3" '
    'fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="12" cy="12" r="3.4" fill="currentColor"/></svg>'
)
ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><style>:root{color:#111}'
    "@media(prefers-color-scheme:dark){:root{color:#f1f1ee}}</style>"
    '<rect x="3" y="3" width="18" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="2.4"/>'
    '<circle cx="12" cy="12" r="3.4" fill="currentColor"/></svg>\n'
)

_PAIRS = dict(zip("абвгдђежзијклмнопрстћуфхцчш", "a b v g d đ e ž z i j k l m n o p r s t ć u f h c č š".split()))
_PAIRS.update({"љ": "lj", "њ": "nj", "џ": "dž"})
_CYRILLIC = re.compile("[Ѐ-ӿ]")


def latin(text: str) -> str:
    """Serbian Cyrillic to Latin. Љ, Њ and Џ become Lj, Nj, Dž, or LJ, NJ, DŽ inside a word in capitals."""
    out = []
    for i, ch in enumerate(text):
        low = ch.lower()
        if low not in _PAIRS:
            out.append(ch)
        elif ch == low:
            out.append(_PAIRS[low])
        else:
            nxt = text[i + 1] if i + 1 < len(text) else ""
            shout = nxt.isalpha() and nxt == nxt.upper() and nxt != nxt.lower()
            out.append(_PAIRS[low].upper() if shout else _PAIRS[low].capitalize())
    return "".join(out)


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def bar(data: dict, script: str) -> str:
    fam = data["family"]
    links = "".join(f'\n    <a href="{esc(s["url"][script])}">{esc(s["name"][script])}</a>' for s in data["sites"])
    return (
        f'<nav class="ju-bar" aria-label="{esc(fam["name"][script])}">\n  <div class="ju-bar-in">\n'
        f'    <a class="ju-name" href="{esc(fam["url"][script])}" aria-current="page">{MARK}{esc(fam["name"][script])}</a>'
        f"{links}\n  </div>\n</nav>"
    )


def foot(data: dict, script: str) -> str:
    fam = data["family"]
    items = "".join(
        f'\n    <li><a href="{esc(s["url"][script])}">{esc(s["name"][script])}</a><span>{esc(s["about"][script])}</span></li>'
        for s in data["sites"]
    )
    return (
        f'<section class="ju-foot" aria-label="{esc(fam["name"][script])}">\n'
        f'  <h2><a href="{esc(fam["url"][script])}">{MARK}{esc(fam["name"][script])}</a></h2>\n'
        f'  <p>{esc(fam["promise"][script])} <a href="#nacela">{esc(fam["principles"][script])}</a></p>\n'
        f"  <ul>{items}\n  </ul>\n</section>"
    )


def cards(data: dict, script: str) -> str:
    """The sites' cards, written in Cyrillic words here and turned with the rest of the page."""
    out = []
    for s in data["sites"]:
        url, shown = esc(s["url"][script]), esc(re.sub(r"^https://|/.*$", "", s["url"]["lat"]))
        out.append(
            f'<article class="site">\n  <h3><a href="{url}">{esc(s["name"]["cyr"])}</a></h3>\n'
            f'  <p>{esc(s["about"]["cyr"])}</p>\n  <p class="source">Извор: {esc(s["source"]["cyr"])}</p>\n'
            f'  <p class="go"><a href="{url}">{shown}</a></p>\n</article>'
        )
    return "\n".join(out)


def page(data: dict, script: str, version: str, built: str) -> str:
    fam = data["family"]
    other = "cyr" if script == "lat" else "lat"
    text = (HERE / "index.html").read_text(encoding="utf-8").replace("@@SITES@@", cards(data, script))
    text = text.replace("@@BUILT@@", built)
    if script == "lat":
        text = latin(text)
    # What follows is put in after the letters are turned: addresses, and the words already in the page's script.
    for key, value in {
        "@@LANG@@": "sr-Latn" if script == "lat" else "sr-Cyrl",
        "@@LANG_OTHER@@": "sr-Cyrl" if script == "lat" else "sr-Latn",
        "@@OTHER@@": "Ћирилица" if script == "lat" else "Latinica",
        "@@ROOT@@": "" if script == "lat" else "../",
        "@@V@@": version,
        "@@URL_LAT@@": esc(fam["url"]["lat"]),
        "@@URL_CYR@@": esc(fam["url"]["cyr"]),
        "@@URL_SELF@@": esc(fam["url"][script]),
        "@@URL_OTHER@@": "cir/" if script == "lat" else "../",
        "@@PROMISE@@": esc(fam["promise"][script]),
        "@@MARK@@": MARK,
        "@@BAR@@": bar(data, script),
        "@@FOOT@@": foot(data, script),
    }.items():
        text = text.replace(key, value)
    return text


def check(text: str, script: str, data: dict) -> list[str]:
    """What is wrong with a built page; nothing when it may be published."""
    wrong = []
    if "@@" in text:
        wrong.append("a placeholder was left in")
    loads = re.findall(r'<(?:script|img|iframe|source|video|audio|embed|object)\b[^>]*\b(?:src|data)="([^"]*)"', text)
    loads += re.findall(r'<link\b(?![^>]*rel="(?:alternate|canonical)")[^>]*\bhref="([^"]*)"', text)
    for address in loads:
        if re.match(r"(?:[a-z]+:)?//", address):
            wrong.append(f"loads from another server: {address}")
    if "<script" in text:
        wrong.append("the page has a script; it needs none")
    if script == "lat":
        left = _CYRILLIC.findall(text.replace("Ћирилица", ""))
        if left:
            wrong.append("Cyrillic letters on the Latin page: " + "".join(sorted(set(left))))
    for s in data["sites"]:
        if text.count(s["url"][script]) < 3:
            wrong.append(f'{s["id"]} is not in the bar, the cards and the footer')
    return wrong


def build(out: Path) -> list[str]:
    data = json.loads((DESIGN / "sites.json").read_text(encoding="utf-8"))
    styles = (DESIGN / "osnova.css").read_bytes() + (HERE / "site.css").read_bytes()
    version = hashlib.sha256(styles).hexdigest()[:8]
    today = datetime.date.today()
    built = f"{today.day}. {today.month}. {today.year}."
    if out.exists():
        shutil.rmtree(out)
    (out / "cir").mkdir(parents=True)
    shutil.copy(DESIGN / "osnova.css", out / "osnova.css")
    shutil.copytree(DESIGN / "fonts", out / "fonts")
    shutil.copy(HERE / "site.css", out / "site.css")
    (out / "znak.svg").write_text(ICON, encoding="utf-8", newline="\n")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    wrong = []
    for script, where in (("lat", out / "index.html"), ("cyr", out / "cir" / "index.html")):
        text = page(data, script, version, built)
        where.write_text(text, encoding="utf-8", newline="\n")
        wrong += [f"{where.relative_to(out).as_posix()}: {w}" for w in check(text, script, data)]
    for sheet in (DESIGN / "osnova.css", HERE / "site.css"):
        for address in re.findall(r"url\(([^)]*)\)", sheet.read_text(encoding="utf-8")):
            if re.match(r"""['"]?(?:[a-z]+:)?//""", address):
                wrong.append(f"{sheet.name}: loads from another server: {address}")
    return wrong


def main() -> int:
    args = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    args.add_argument("--out", default="_site", type=Path)
    out = args.parse_args().out
    wrong = build(out)
    for w in wrong:
        print("build:", w, file=sys.stderr)
    if not wrong:
        print(f"build: {out}/index.html and {out}/cir/index.html")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
