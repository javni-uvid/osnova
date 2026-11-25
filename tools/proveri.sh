#!/bin/sh
# This repository's own checks (posalji.sh runs them, and the test workflow): every script parses, every
# workflow, the template's too, passes actionlint and zizmor, the list of municipalities keeps its shape
# (tools/sites.py), the cleanup keeps a worktree an agent is in (tools/test_pocisti.py), and Javni uvid's own page builds (the build fails when a page would load anything from
# another server or leaves a site of the family out).
set -eu
for f in tools/*.sh shared/tools/*.sh shared/tools/hooks/* template/tools/*.sh template/tools/hooks/*; do sh -n "$f"; done
uvx --from actionlint-py==1.7.12.25 actionlint -shellcheck= -pyflakes= .github/workflows/*.yml template/.github/workflows/*.yml
uvx zizmor==1.32.0 --format plain --config .github/zizmor.yml .github/workflows/ template/.github/workflows/
uv run --no-project tools/sites.py check
uv run --no-project tools/test_sites.py
uv run --no-project tools/test_pocisti.py
out=$(mktemp -d)
uv run --no-project site/build.py --out "$out/site"
rm -rf "$out"
echo "proveri: sve je u redu."
