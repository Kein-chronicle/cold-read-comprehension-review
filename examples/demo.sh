#!/usr/bin/env bash
cd "$(dirname "$0")/.."
run() { printf '$ %s\n' "$*"; "$@"; printf '[exit %s]\n\n' "$?"; }
echo "# Two independent readers who saw only the video/page, graded against the author's truth file"
run python3 scripts/grade.py examples/truth.json examples/reader-1.json examples/reader-2.json
echo "# One of them reports a severe confusion"
run python3 scripts/grade.py examples/truth.json examples/reader-1.json examples/reader-confused.json
echo "# One reader is not independent evidence"
run python3 scripts/grade.py examples/truth.json examples/reader-1.json
