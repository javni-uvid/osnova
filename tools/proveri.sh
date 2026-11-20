#!/bin/sh
# This repository's own checks (posalji.sh runs them, and the test workflow): every script parses, and every
# workflow, the template's too, passes actionlint and zizmor.
set -eu
for f in tools/*.sh tools/hooks/*; do sh -n "$f"; done
uvx --from actionlint-py==1.7.12.25 actionlint -shellcheck= -pyflakes= .github/workflows/*.yml template/.github/workflows/*.yml
uvx zizmor==1.32.0 --format plain --config .github/zizmor.yml .github/workflows/ template/.github/workflows/
echo "proveri: sve je u redu."
