"""tools/sites.py without the network (tools/proveri.sh: `uv run --no-project tools/test_sites.py`)."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sites  # noqa: E402


def test_variants():
    assert sites.variants("valjevo.org.rs") == ["valjevo.rs", "valjevo.ls.gov.rs", "valjevo.gov.rs"]
    assert sites.variants("bojnik.ls.gov.rs")[0] == "bojnik.rs"
    assert sites.variants("grad.zrenjanin.rs") == []
    assert sites.variants("aleksinac.org") == []


def test_look_moves_a_domain_that_doesnt_answer():
    up = {"https://valjevo.rs/", "https://primer.rs/"}

    def fetcher(url):
        if url not in up:
            raise OSError("down")

    rows = [{"municipality_code": "70017", "name": "Пример", "domain": "primer.rs", "note": "rik-adresar"},
            {"municipality_code": "70025", "name": "Ваљево", "domain": "valjevo.org.rs", "note": "rik-adresar"},
            {"municipality_code": "70033", "name": "Друга", "domain": "druga.rs", "note": ""},
            {"municipality_code": "70041", "name": "Трећа", "domain": "", "note": "webmail"}]
    logged = []
    assert sites.look(rows, "2026-11-22", logged.append, fetcher, lambda s: None) == 1
    assert rows[0]["domain"] == "primer.rs"
    assert rows[1]["domain"] == "valjevo.rs"
    assert rows[1]["note"] == "rik-adresar; was valjevo.org.rs, found by the sites workflow 2026-11-22"
    assert rows[2]["domain"] == "druga.rs" and rows[2]["note"] == ""
    assert logged[-1] == "3 sites asked for, 1 moved, 1 not answering"


def test_the_list_and_its_check():
    assert sites.problems() == []
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "m.csv"
        sites.save([{"municipality_code": "7001", "name": "", "domain": "https://a.rs/", "note": ""},
                    {"municipality_code": "7001", "name": "Б", "domain": "", "note": ""}], p)
        found = sites.problems(p)
        assert len(found) == 5, found  # the code twice (not five digits), again, no name, not bare
        assert sites.load(p)[1]["name"] == "Б"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("test_sites: u redu.")
