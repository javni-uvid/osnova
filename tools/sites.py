"""The family's list of municipalities (shared/data/municipalities.csv): its shape checked, and its sites looked at.

`check` (tools/proveri.sh): the columns, one row per code, a code of five digits (or r and RIK's number), a name, a domain without a
scheme or path. `look` (the weekly **sites** workflow): each domain's front page is asked for; a domain that
doesn't answer is looked for under its other spellings (`variants`), and the one that answers replaces it, the
old one named in the note, so the file stays the record of where to look. One request per site and spelling.

Moved here from javni-uvid/izborna-analiza's weekly watch (22 Nov 2026), where it was found that a commission's
e-mail domain is not always the municipality's site (Valjevo: valjevo.org.rs, the site valjevo.rs).
Standard library only: `uv run --no-project tools/sites.py check|look`.
"""
from __future__ import annotations

import csv
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

LIST = Path(__file__).resolve().parent.parent / "shared" / "data" / "municipalities.csv"
COLUMNS = ["municipality_code", "name", "domain", "note"]
# a browser-like start, as some municipal sites refuse a bare client name (403), and who we are after it
AGENT = "Mozilla/5.0 (compatible; javni-uvid; +https://javni-uvid.github.io/osnova/)"
PAUSE = 0.5  # seconds between requests
DOMAIN = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$")


def load(path: Path = LIST) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def save(rows: list[dict], path: Path = LIST) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def problems(path: Path = LIST) -> list[str]:
    with open(path, encoding="utf-8", newline="") as f:
        header = next(csv.reader(f), [])
    if header != COLUMNS:
        return [f"the columns are {header}, not {COLUMNS}"]
    out, seen = [], set()
    for i, r in enumerate(load(path), start=2):
        code = r["municipality_code"]
        if not re.fullmatch(r"\d{5}|r\d+", code):
            out.append(f"line {i}: the code {code!r} is neither five digits nor r and RIK's number")
        if code in seen:
            out.append(f"line {i}: the code {code} again")
        seen.add(code)
        if not r["name"]:
            out.append(f"line {i}: no name")
        if r["domain"] and not DOMAIN.match(r["domain"]):
            out.append(f"line {i}: {r['domain']!r} is not a bare domain (no https://, no path, lower case)")
    return out


def fetch(url: str, timeout: int = 45) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept-Language": "sr"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        r.read(1)


def answers(domain: str, fetcher=fetch, sleep=time.sleep) -> bool:
    """The front page answers: https, then www, then plain http (old sites)."""
    for url in (f"https://{domain}/", f"https://www.{domain}/", f"http://{domain}/", f"http://www.{domain}/"):
        try:
            fetcher(url)
            return True
        except Exception:  # noqa: BLE001 - the next spelling
            continue
        finally:
            sleep(PAUSE)
    return False


def variants(domain: str) -> list[str]:
    """Other spellings of a municipality's site: the same name under .rs, .org.rs, .ls.gov.rs and .gov.rs."""
    d = domain.lower().removeprefix("www.")
    for tail in (".ls.gov.rs", ".org.rs", ".gov.rs", ".rs"):
        if d.endswith(tail):
            base = d[: -len(tail)]
            break
    else:
        return []
    if "." in base:  # grad.zrenjanin.rs, obrenovac.bg.ls.gov.rs: a name inside another; left as it is
        return []
    return [f"{base}{t}" for t in (".rs", ".org.rs", ".ls.gov.rs", ".gov.rs") if f"{base}{t}" != d]


def look(rows: list[dict], today: str, log=print, fetcher=fetch, sleep=time.sleep) -> int:
    """Every domain asked for; one that doesn't answer replaced by a spelling that does. Returns how many moved."""
    moved = down = 0
    for r in rows:
        if not r["domain"] or answers(r["domain"], fetcher, sleep):
            continue
        alt = next((v for v in variants(r["domain"]) if answers(v, fetcher, sleep)), None)
        if alt is None:
            down += 1
            log(f"{r['municipality_code']}: {r['domain']} doesn't answer, nor does another spelling")
            continue
        log(f"{r['municipality_code']}: {r['domain']} doesn't answer, {alt} does")
        r["note"] = (r["note"] + f"; was {r['domain']}, found by the sites workflow {today}").strip("; ")
        r["domain"] = alt
        moved += 1
    log(f"{sum(1 for r in rows if r['domain'])} sites asked for, {moved} moved, {down} not answering")
    return moved


def main(argv: list[str]) -> int:
    what = argv[1] if len(argv) > 1 else ""
    if what == "check":
        found = problems()
        for p in found:
            print(f"{LIST.name}: {p}")
        return 1 if found else 0
    if what == "look":
        rows = load()
        if look(rows, date.today().isoformat()):
            save(rows)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
