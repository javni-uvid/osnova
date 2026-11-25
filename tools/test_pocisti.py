"""shared/tools/pocisti.sh and agenti.py without Orca or GitHub (tools/proveri.sh: `uv run --no-project
tools/test_pocisti.py`): real worktrees of a throwaway repository, and stand-ins for `gh` and `orca`."""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "shared" / "tools"
sys.path.insert(0, str(TOOLS))
import agenti  # noqa: E402

NOW = 1795600000.0
W = "C:/w/task"


def agent(state="done", silent=0.0, live=True, **more):
    return {"address": "term_a", "agentType": "claude", "state": state, "updatedAt": (NOW - silent) * 1000,
            "hasLivePty": live, **more}


def ps(*agents, path=W, **more):
    return {"ok": True, "result": {"worktrees": [{"path": path, "agents": list(agents)}], "truncated": False, **more}}


def terms(*rows, **more):
    return {"ok": True, "result": {"terminals": list(rows), "truncated": False, **more}}


def term(identity=None, handle="term_a", path=W, **more):
    return {"handle": handle, "worktreePath": path, "connected": True, "agentIdentity": identity, **more}


def keeps(p, t, worktree=W):
    return agenti.keeps(worktree, p, t, NOW)


def test_nobody_in_it():
    assert keeps(ps(), terms()) == ""
    assert keeps(ps(), terms(term())) == ""  # the shell Orca opens in every worktree
    assert keeps(ps(), terms(term("claude", path="C:/w/other"))) == ""


def test_an_open_agent_keeps_it_working_waiting_or_idle():
    for state in ("working", "waiting", "blocked", "done", None):
        assert keeps(ps(agent(state)), terms(term("claude")))
    assert keeps(ps(agent("working", silent=9e5)), terms(term("claude")))
    assert keeps(ps(agent("waiting", silent=9e5)), terms(term("claude")))
    assert keeps(ps(agent("done", silent=agenti.QUIET - 60)), terms(term("claude")))


def test_a_day_done_and_silent_or_gone_keeps_it_no_more():
    old = agenti.QUIET + 60
    assert keeps(ps(agent("done", silent=old)), terms(term("claude"))) == ""
    assert keeps(ps(agent("working", silent=old, live=False)), terms()) == ""
    assert keeps(ps(agent("working", silent=60, live=False)), terms())
    assert keeps(ps(agent("done", silent=old), agent("working", address="term_b")), terms(term("claude")))  # another one


def test_a_terminal_with_an_agent_the_summary_lacks_keeps_it():
    assert keeps(ps(), terms(term("codex")))
    assert keeps(ps(agent("done", silent=9e5)), terms(term("claude"), term("claude", handle="term_b")))
    assert keeps(ps(), terms(term("claude", path="", worktreeId="1-2::" + W)))
    assert keeps(ps(), terms(term("claude", connected=False))) == ""


def test_paths_are_the_same_however_written():
    assert keeps(ps(agent("working"), path="c:\\W\\task\\"), terms())
    assert keeps(ps(), terms(term("claude", path="c:\\W\\task")))


def test_what_cant_be_told_keeps_it():
    good_p, good_t = ps(), terms()
    for bad in (None, [], {}, "x", {"ok": False, "result": good_p["result"]}, {"ok": True}, {"ok": True, "result": []}):
        assert keeps(bad, good_t) and keeps(good_p, bad), bad
    assert keeps(ps(truncated=True), good_t) and keeps(good_p, terms(truncated=True))
    assert keeps(ps(path="C:/w/other"), good_t)  # Orca doesn't know the worktree
    p = copy.deepcopy(good_p)
    for agents in (None, "x", [1]):
        p["result"]["worktrees"][0]["agents"] = agents
        assert keeps(p, good_t)
    assert keeps(ps(agent("done", updatedAt="x")), good_t)  # when, isn't known


def run(*cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8").stdout.strip()


class Repo:
    """A main clone with worktrees, each on a "merged" pull request's head."""

    def __init__(self, d: Path, names):
        self.d, self.main, self.bin = d, d / "main", d / "bin"
        self.main.mkdir()
        self.bin.mkdir()
        run("git", "init", "-q", "-b", "main", cwd=self.main)
        run("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x", cwd=self.main)
        for n in names:
            run("git", "worktree", "add", "-q", "-b", n, str(d / n), cwd=self.main)
        self.head = run("git", "rev-parse", "HEAD", cwd=self.main)
        self.merged = list(names)
        # The names as git writes them: that is what pocisti.sh compares and Orca is asked about.
        out = run("git", "worktree", "list", "--porcelain", cwd=self.main)
        self.path = {p.rsplit("/", 1)[-1]: p for p in (x[9:] for x in out.splitlines() if x.startswith("worktree "))}
        self.ps = ps()
        self.ps["result"]["worktrees"] = [{"path": p, "agents": []} for p in self.path.values()]
        self.terms, self.fails = terms(), False

    def agent(self, name, **kw):
        for w in self.ps["result"]["worktrees"]:
            if w["path"] == self.path[name]:
                w["agents"].append({**agent(**kw), "updatedAt": time.time() * 1000})

    def clean(self, *args, frm="own"):
        (self.d / "merged").write_text("".join(f"{n} {self.head}\n" for n in self.merged), encoding="utf-8")
        (self.d / "ps.json").write_text(json.dumps(self.ps), encoding="utf-8")
        (self.d / "t.json").write_text(json.dumps(self.terms), encoding="utf-8")
        d = self.d.as_posix()
        (self.bin / "gh").write_text(f'#!/bin/sh\ncat "{d}/merged"\n', encoding="utf-8", newline="\n")
        (self.bin / "orca").write_text(
            "#!/bin/sh\n" + ("exit 1\n" if self.fails else "") +
            f'case "$1 $2" in\n"worktree ps") cat "{d}/ps.json" ;;\n"terminal list") cat "{d}/t.json" ;;\n'
            f'"worktree rm") git -C "{d}/main" worktree remove "${{4#path:}}" ;;\n*) exit 1 ;;\nesac\n', encoding="utf-8", newline="\n")
        for f in self.bin.iterdir():
            f.chmod(0o755)
        env = {**os.environ, "PATH": str(self.bin) + os.pathsep + os.environ["PATH"]}
        r = subprocess.run([shutil.which("sh"), (TOOLS / "pocisti.sh").as_posix(), *args], cwd=self.d / frm, env=env,
                           capture_output=True, text=True, encoding="utf-8", timeout=120)
        assert r.returncode == 0, r.stderr
        return r.stdout

    def there(self):
        return {n for n in self.path if (self.d / n).is_dir()}


def with_repo(names, f):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        f(Repo(Path(d).resolve(), names))


def test_the_cleanup_removes_what_is_merged_and_empty_only():
    def f(r):
        r.agent("busy", state="working")
        r.agent("idle", state="done")
        run("git", "worktree", "lock", "--reason", "why", str(r.d / "locked"), cwd=r.main)
        (r.d / "dirty" / "x").write_text("x")
        r.merged.remove("open")
        before = r.there()
        said = r.clean("--proba")
        assert r.there() == before
        assert said.count("bi uklonio") == 2 and r.path["free"] in said and r.path["free2"] in said
        assert said.count("ostaje") == 3 and "agent claude (working" in said and "zaključan" in said
        said = r.clean()
        assert r.there() == before - {"free", "free2"} and said.count("uklonjen") == 2 and said.count("ostaje") == 3, said
        run("git", "worktree", "unlock", str(r.d / "locked"), cwd=r.main)
        for w in r.ps["result"]["worktrees"]:
            w["agents"] = []  # the agents were closed
        r.clean()
        assert r.there() == {"main", "own", "dirty", "open"}
    with_repo(["own", "busy", "free", "idle", "locked", "dirty", "open", "free2"], f)


def test_nothing_goes_when_orca_doesnt_answer():
    def f(r):
        r.fails = True
        assert "Orca se ne javlja" in r.clean() and r.there() == {"main", "own", "free"}
        r.fails, r.ps = False, {"ok": False}
        assert "ostaje" in r.clean() and r.there() == {"main", "own", "free"}
    with_repo(["own", "free"], f)


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print("ok", name)
