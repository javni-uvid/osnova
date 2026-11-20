# osnova

Zajednička osnova projekata organizacije [javni-uvid](https://github.com/javni-uvid): načela koja svaki projekat
obećava čitaocima, pravila rada, bezbednost i alati. Projekti ostaju samostalni repozitorijumi i odavde preuzimaju
kopiju.

The shared base of the javni-uvid projects: the principles every project promises its readers, the rules of
work, security, and the tools. Each project stays a repository of its own and takes a copy from here.

| Project | What it is |
|---|---|
| [zailiprotiv](https://github.com/javni-uvid/zailiprotiv) | How the MPs of Serbia's National Assembly vote, since 2012 |
| [izborna-analiza](https://github.com/javni-uvid/izborna-analiza) | Every results file of Serbia's electoral commission kept, and every polling station checked by the same rules |

## What is here

| Path | What |
|---|---|
| `shared/principles.md` | The promises every project makes to its readers. Changed by the maintainer only. |
| `shared/work.md` | How to work in a project: a branch and a pull request per task, tests, decisions written down. |
| `shared/security.md` | What every project guards and how; the settings a new repository gets. |
| `tools/` | `posalji.sh` (a task's branch to `main`), `pocisti.sh` (merged worktrees removed), the pre-push hook. |
| `template/` | What a project copies once: the **osnova** workflow. |
| `projects.txt` | The projects that take the copy. |

## How a project takes it

A project has the **osnova** workflow (`template/.github/workflows/osnova.yml`). Daily, and when started by hand,
it copies `shared/` into the project's `osnova/` folder and commits it. So an agent working in a project, and a
workflow running there, have the rules in that repository; nobody has to look here first.

A project's own AGENTS.md holds what is only its own, and its own principles. It may be stricter than what is
here. Where it differs on purpose, it says so with the date of the maintainer's decision.

## A new project

1. A repository in the organization, public, with the settings of `shared/security.md` ("The repository's
   settings").
2. `template/` copied in; the project added to `projects.txt` and the table above.
3. Its AGENTS.md: what the project is, its own principles, its sources, the map of its decisions' files.
