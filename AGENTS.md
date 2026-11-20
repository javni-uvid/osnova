# AGENTS.md

How to work on this repository. It holds what every javni-uvid project shares (`shared/`), and each project
takes a copy (README.md). The rules of work in `shared/work.md` hold here too; this file adds what is only this
repository's.

- **`shared/principles.md` is the maintainer's.** A pull request that changes it is opened with
  `sh shared/tools/posalji.sh <body file> --ne-spajaj` and left for them to merge. Everything else is merged by the
  agent once **test** passes.
- **What goes here:** a rule, a guard or a tool that holds for every project. What only one project needs stays
  in that project, even when it is well made. Before moving something here, read how the other projects do it
  (`projects.txt`): if they differ for a reason, it isn't shared.
- **Javni uvid's own page is here too** (`site/`, published by **pages** at https://javni-uvid.github.io/osnova/):
  what the family is, its sites and the principles in Serbian, in both scripts. Its text of the principles
  follows `shared/principles.md`: a change of one is a change of the other, and the maintainer's.
  `uv run --no-project site/build.py --out _site` builds it.
- **`shared/design/` is the family's look,** copied to every project with the rest of `shared/`: the font, the
  base colours, the scale of letter sizes, the bar and the footer block (`osnova.css`), and the list of the
  family's sites (`sites.json`). A site added there shows on every other site after its next copy and build. A
  change of the look changes every site: look at the built page here, and say in the pull request what a
  project has to do.
- **`shared/` is read by agents at the start of every task in every project:** keep it short. A rule with its
  reason in a sentence; the story of how it was learned belongs in the project it happened in.
- **After a merge that changes `shared/`,** start the copy in each project rather than wait for the night:
  `for p in $(cat projects.txt); do gh workflow run osnova -R "$p"; done`.
- **A project may be stricter, never looser,** unless its AGENTS.md says so with the date of the maintainer's
  decision. A change here that would make a project's own rule wrong is told in the pull request.
- **The tools are run from `shared/tools/` here** (`git config core.hooksPath shared/tools/hooks`); a project runs
  them through its own `tools/`, which only call the copy in its `osnova/tools/`.
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
- **Javni uvid's own page lives in this repository** (20 Nov 2026, the maintainer's decision, over a repository
  of its own): it is one page, built from what is already here (the sites' list, the principles), and needs no
  data runs. Until the family has a domain its address is https://javni-uvid.github.io/osnova/, kept in
  `shared/design/sites.json` alone, so a domain later is a change of one file.
- **One look for the family: the same font, base colours and scale of sizes on every site, and every site links
  the others** (20 Nov 2026, the maintainer's decision), so that a reader sees the sites come from one place.
  The base is Za ili Protiv's as it stood (Literata for headings, the system font for text, black on white): it
  is the site most read, mostly on phones, and a system font downloads nothing. A site keeps its own colours
  only where they carry its data. A third site links the others through the bar and the footer block, the same
  markup everywhere (`shared/design/family.html`).
