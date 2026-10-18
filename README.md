# cold-read-comprehension-review

**Grade whether a video or page communicates, using independent cold readers checked against the author's truth file, and flag stale judgements.**

[![test](https://github.com/Kein-chronicle/cold-read-comprehension-review/actions/workflows/test.yml/badge.svg)](https://github.com/Kein-chronicle/cold-read-comprehension-review/actions/workflows/test.yml) ![license](https://img.shields.io/badge/license-MIT-blue.svg) ![dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)

## Why

The author cannot judge their own explanation. Give two readers only the finished artifact, ask what it claims, which steps it shows and what the result looks like, and grade their answers against what you meant. Confusions are reported with a severity; a single reader is refused.

## Install

**As a Claude Code skill** (Claude uses it when the task matches the skill description):

```sh
git clone https://github.com/Kein-chronicle/cold-read-comprehension-review.git ~/.claude/skills/cold-read-review
```

For a single project, clone into `<project>/.claude/skills/cold-read-review` instead, then start a new Claude Code session.

**As plain scripts:**

```sh
git clone https://github.com/Kein-chronicle/cold-read-comprehension-review.git
cd cold-read-comprehension-review
```

**Requires:** Python 3.10+.

## Quick start

Grade three readers:

```console
$ bash examples/demo.sh
# Two independent readers who saw only the video/page, graded against the author's truth file
$ python3 scripts/grade.py examples/truth.json examples/reader-1.json examples/reader-2.json
examples/reader-1.json
  [PASS] claim recovered
  [PASS] steps recovered
  [PASS] result recovered
  [PASS] structure recovered
  [PASS] no severe confusion
  [PASS] no required field unknown
examples/reader-2.json
  [PASS] claim recovered
  [PASS] steps recovered
  [PASS] result recovered
  [PASS] structure recovered
  [PASS] no severe confusion
  [PASS] no required field unknown
COLD READ PASS
[exit 0]

# One of them reports a severe confusion
$ python3 scripts/grade.py examples/truth.json examples/reader-1.json examples/reader-confused.json
examples/reader-1.json
  [PASS] claim recovered
  [PASS] steps recovered
  [PASS] result recovered
  [PASS] structure recovered
  [PASS] no severe confusion
  [PASS] no required field unknown
examples/reader-confused.json
  [PASS] claim recovered
  [PASS] steps recovered
  [PASS] result recovered
  [PASS] structure recovered
  [FAIL] no severe confusion
  [PASS] no required field unknown
COLD READ FAIL
[exit 1]

# One reader is not independent evidence
$ python3 scripts/grade.py examples/truth.json examples/reader-1.json
need at least two readers: one lucky reader proves little
[exit 2]
```

The output above is real: it is produced by the files in `examples/`.

## Use it on your own files

```sh
python3 scripts/grade.py truth.json reader-1.json reader-2.json
python3 scripts/staleness.py judgement.json out.mp4
```

Sample inputs for every file format are in `examples/` and `tests/`; the details are in [SKILL.md](SKILL.md).

## What it checks

- `grade.py truth.json reader-1.json reader-2.json ...` checks claim, steps, result keywords, section structure, severe confusions and unknown required fields. Exit `0` only if every reader passes every check.
- `staleness.py judgement.json artifact [--stamp]`: with `--stamp` it records a content hash in the judgement so later checks compare content (files and whole folders); without one only modification times are compared. Exit `1` stale, `3` cannot establish freshness.
- `references/reader-prompt.md` is the prompt skeleton for the readers.

## Limits

- Reader quality sets the ceiling: use blind, independent readers.

## More from the same collection

Small, tested tools that grew out of running AI agents and game/app pipelines for months:

- [**canvas-render-pixel-gate**](https://github.com/Kein-chronicle/canvas-render-pixel-gate): Detect grey-box screenshots: measure unique colors and flat-fill share of a rendered game canvas, and refuse to pass what it could not measure.
- [**web-game-asset-reality-check**](https://github.com/Kein-chronicle/web-game-asset-reality-check): Catch web-game bugs the type checker can't: fonts that are declared but not shipped, runtime CDN dependencies, and page errors from headless Chromium.
- [**ffmpeg-video-qa-gates**](https://github.com/Kein-chronicle/ffmpeg-video-qa-gates): Machine QA for short videos with ffmpeg: frozen frames, dead air, loudness, true peak, size, a busy opening, and readable subtitle timing.

## Development

```sh
python3 tests/test_grade.py
```

The tests include inputs that are supposed to be rejected, so a green run also shows the checks can fail. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

If this saved you a debugging session, a star helps other people find it. Bug reports and failing test cases are even better.

<sub>Keywords: review, usability, ai-agents, llm-evaluation, content-qa, claude-code, claude-skills, agent-skills</sub>
