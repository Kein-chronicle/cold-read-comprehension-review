---
name: cold-read-review
description: Verify that a viewer/reader actually understands a deliverable (video, article, onboarding page, landing page) by giving it to isolated readers with no memory and grading their structured answers with code, not with another opinion. Use when "it passes all checks but people are confused", when you need an independent comprehension gate, when AI-produced content must be reviewed without the author's context, or when stale approvals must expire after the artifact changes.
---

# cold-read-review

Numbers can't measure "does it make sense". A cold reader can - if you stop the reader from grading itself.

## Protocol

1. **Isolate.** Run readers in a fresh session with no memory, no repo, read-only tools. Give them ONLY what the
   audience gets (frames at fixed interval, transcript, title/description/pinned comment). Never the plan or intent.
2. **Make them answer in JSON** with a fixed schema: summary, situation, claim, steps[], result, sections[],
   `how_to_get_X`, `confusions[{text, severity: severe|minor}]`. Rule in the prompt: "if the material gives no
   basis, write `unknown`; do not guess."
3. **Grade with code.** Compare answers to ground truth you wrote beforehand (keyword sets per video, a number that
   must be recovered, minimum number of sections, zero severe confusions, no required field `unknown`).
   The reader never says pass/fail.
4. **Two readers, both must pass.** One lucky reader proves little.
5. **Expire stale passes.** A judgement older than the artifact file is "needs re-review", not a pass
   (`scripts/staleness.py`).
6. **Define `severe` narrowly** in the reader prompt: only "makes the promised result or the usage order
   impossible to understand". Without that, design choices get reported as defects forever.
7. **Declare intended design** the reader may find odd (e.g. "the full prompt is deliberately in the pinned comment").

## Known limits (write them in the judgement file)

- If readers are the same model family as the producer, independence is weak. Record the model name in the output.
- It tests comprehension of what you *thought to ask*. Keep adding questions when real viewers get confused.
- Keyword grading can false-FAIL a correct paraphrase. When that happens, widen the keyword set per artifact
  (`reader_keys` in the scenario), and log it - see "criteria change log" below.

## Criteria change log (honesty rule)

Whenever a failing gate leads to a change, record whether you fixed **the artifact** or **the criterion**, and why.
Legit criterion fixes go "down to the intent" (narrow what you ban, with a forgery test that still catches the
real thing). Illegit: loosening until it passes. In the source project, one failing "quote card label" confused
readers about who was speaking -> the *video* was changed; one keyword that false-flagged an innocent
expense item -> the *rule* was narrowed and a test added that catches requests but passes expenses.

## Truth file and reader file

`truth.json` must contain at least one of `claim_any`, `claim_all`, `steps_all_of`, `result_keywords`, `min_sections`, `how_to_get_any` (plus optional `result_min_hits`, `required_fields`); unknown keys are rejected.
Readers answer `summary`, `claim_seen`, `steps[]`, `result_seen`, `sections[]`, `confusions[{text, severity}]`. A confusion without a severity or with any severity other than `minor`/`low`/`trivial` counts as severe.
Two identical reader files are rejected as one reader. `staleness.py judgement.json artifact --stamp` records a content hash so later freshness checks compare content (exit `3` = cannot establish freshness).

## Use

`scripts/grade.py` grades reader JSON against a truth file; `scripts/staleness.py` flags old judgements.
```bash
python3 scripts/grade.py truth.json reader-1.json reader-2.json     # exit 0 only if every reader passes every check
python3 scripts/staleness.py judgement.json artifact.mp4            # exit 1 if the artifact is newer than the judgement
python3 tests/test_grade.py
```
Prompt skeleton: `references/reader-prompt.md`.
