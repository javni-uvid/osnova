# AGENTS.md

How to work on this repository. It holds what every javni-uvid project shares (`shared/`), and each project
takes a copy (README.md). The rules of work in `shared/work.md` hold here too; this file adds what is only this
repository's.

- **`shared/principles.md` is the maintainer's.** A pull request that changes it is opened with
  `sh tools/posalji.sh <body file> --ne-spajaj` and left for them to merge. Everything else is merged by the
  agent once **test** passes.
- **What goes here:** a rule, a guard or a tool that holds for every project. What only one project needs stays
  in that project, even when it is well made. Before moving something here, read how the other projects do it
  (`projects.txt`): if they differ for a reason, it isn't shared.
- **`shared/` is read by agents at the start of every task in every project:** keep it short. A rule with its
  reason in a sentence; the story of how it was learned belongs in the project it happened in.
- **After a merge that changes `shared/`,** start the copy in each project rather than wait for the night:
  `for p in $(cat projects.txt); do gh workflow run osnova -R "$p"; done`.
- **A project may be stricter, never looser,** unless its AGENTS.md says so with the date of the maintainer's
  decision. A change here that would make a project's own rule wrong is told in the pull request.
- **Tests:** `sh tools/proveri.sh` (the scripts parse, the workflows pass actionlint and zizmor). The **test**
  workflow runs it on every pull request and on `main`.
- **Talk to the maintainer in Serbian** (Latin script), briefly. Code, comments and docs are in English.

## Decisions

- **Projects are repositories of their own, and take a copy** (20 Nov 2026, the maintainer's decision). Not one
  repository for all (each project has its own data runs, pages, domain and secrets), and not submodules (a
  project gets a commit every hour, so a pointer to it is always behind, and worktrees handle submodules badly).
- **The copy is committed by the project's own workflow, straight to `main`** (20 Nov 2026). A push from here
  would need a token that writes to every project; the project's own token needs nothing new. The maintainer
  decided that a change of the rules reaches the projects without another approval, and a change of the
  principles is approved once, here.
- **The principles here are the common core;** each project keeps its own list whole in its AGENTS.md, in its own
  words (20 Nov 2026). Two projects differ on purpose: zailiprotiv names MPs, public officials, by what they do
  in office; izborna-analiza records no person's name at all.
