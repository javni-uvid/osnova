# osnova

Zajednička osnova projekata [Javnog uvida](https://javni-uvid.github.io/osnova/) (organizacija [javni-uvid](https://github.com/javni-uvid)): načela koja svaki projekat
obećava čitaocima, pravila rada, bezbednost i alati. Projekti ostaju samostalni repozitorijumi i odavde preuzimaju
kopiju.

The shared base of the javni-uvid projects: the principles every project promises its readers, the rules of
work, security, and the tools. Each project stays a repository of its own and takes a copy from here.

| Project | What it is |
|---|---|
| [zailiprotiv](https://github.com/javni-uvid/zailiprotiv) | How the MPs of Serbia's National Assembly vote, since 2012 |
| [izborna-analiza](https://github.com/javni-uvid/izborna-analiza) | Every results file of Serbia's electoral commission kept, and every polling station checked by the same rules |
| [ucestvuj](https://github.com/javni-uvid/ucestvuj) | How a person takes part in decisions where they live: guides, deadlines and addresses (started 20 Nov 2026; no site yet) |

## What is here

| Path | What |
|---|---|
| `shared/principles.md` | The promises every project makes to its readers. Changed by the maintainer only. |
| `shared/work.md` | How to work in a project: a branch and a pull request per task, tests, decisions written down. |
| `shared/security.md` | What every project guards and how; the settings a new repository gets. |
| `shared/tools/` | `posalji.sh` (a task's branch to `main`), `pocisti.sh` (merged worktrees removed), the pre-push hook. |
| `shared/design/` | The family's look, the same on every site: font, base colours, the bar and the footer block that link the sites, and the list of the sites. |
| `shared/data/` | What more than one project needs, kept once: the municipalities (the code every project names one by) and their sites, looked at weekly by the **sites** workflow (`tools/sites.py`). |
| `site/` | Javni uvid's own page, https://javni-uvid.github.io/osnova/: the sites and the principles, in Serbian. |
| `template/` | What a project copies once: the **osnova** workflow, and `tools/` whose scripts only call the copy's. |
| `projects.txt` | The projects that take the copy. |

## How a project takes it

A project has the **osnova** workflow (`template/.github/workflows/osnova.yml`). Daily, and when started by hand,
it copies `shared/` into the project's `osnova/` folder and commits it. The project's `tools/posalji.sh`,
`tools/pocisti.sh` and `tools/hooks/pre-push` are one line each: they run the copy's, so a fix here reaches every
project. So an agent working in a project, and a
workflow running there, have the rules in that repository; nobody has to look here first.

A project's own AGENTS.md holds what is only its own, and its own principles. It may be stricter than what is
here. Where it differs on purpose, it says so with the date of the maintainer's decision.

## A new project

1. A repository in the organization, public, with the settings of `shared/security.md` ("The repository's
   settings").
2. `template/` copied in; the project added to `projects.txt` and the table above.
3. Its AGENTS.md: what the project is, its own principles, its sources, the map of its decisions' files.
4. Its site takes the family's look (`shared/design/README.md`), and the site is added to
   `shared/design/sites.json`, which puts it on Javni uvid's page and on every other site.
