#!/usr/bin/env python3
"""Grade cold-reader JSON answers against ground truth. The reader never decides pass/fail.
usage: grade.py truth.json reader.json [reader2.json ...]     exit 0 every reader passes | 1 a reader fails | 2 bad input (never a pass)
truth.json: {"claim_any":[..],"claim_all":[..],"steps_all_of":[[kw..],[kw..]],"result_min_hits":2,"result_keywords":[..],
             "min_sections":4,"required_fields":["summary","claim_seen","result_seen"],"how_to_get_any":[..]}
reader.json: {"summary":"..","claim_seen":"..","steps":[".."],"result_seen":"..","sections":[".."],"confusions":[{"text":"..","severity":"minor|severe"}]}
Keywords match case-insensitively at the start of a word (so 'send' also matches 'sender': widen or narrow your keywords knowing that); non-ASCII keywords match as substrings."""
import hashlib, json, re, sys

GRADING_KEYS = {"claim_any", "claim_all", "steps_all_of", "result_keywords", "min_sections", "how_to_get_any"}
OTHER_KEYS = {"result_min_hits", "required_fields"}
MINOR = {"minor", "low", "trivial"}                 # anything else (including a missing severity) counts as severe: fail closed


def bad(msg):
    print(f"bad input: {msg}"); sys.exit(2)


def has(text, kws):
    t = str(text).lower()
    for k in kws:
        k = str(k).lower()
        if not k: continue
        if k.isascii():
            if re.search(r"\b" + re.escape(k), t): return True
        elif k in t: return True
    return False


def grade(t, a):
    c = {}
    if "parse_error" in a:
        return {"parseable": False}
    claim = (str(a.get("summary", "")) + " " + str(a.get("claim_seen", "")))
    steps_list = [str(x) for x in a.get("steps", [])] if isinstance(a.get("steps", []), list) else []
    steps = " ".join(steps_list)
    if "claim_any" in t: c["claim recovered"] = has(claim, t["claim_any"])
    if "claim_all" in t: c["claim has required facts"] = all(has(claim, [k]) for k in t["claim_all"])
    if "steps_all_of" in t: c["steps recovered"] = all(has(steps, grp) for grp in t["steps_all_of"]) and len(steps_list) > 0
    if "result_keywords" in t:
        hits = sum(1 for k in t["result_keywords"] if has(a.get("result_seen", ""), [k]))
        c["result recovered"] = hits >= t.get("result_min_hits", 2)
    if "min_sections" in t:
        secs = a.get("sections", []); c["structure recovered"] = isinstance(secs, list) and sum(1 for s in secs if str(s).strip()) >= t["min_sections"]
    if "how_to_get_any" in t: c["access path recovered"] = has(a.get("how_to_get_prompt", ""), t["how_to_get_any"])
    conf = a.get("confusions", []); conf = conf if isinstance(conf, list) else []
    def severe(x): return not (isinstance(x, dict) and str(x.get("severity", "")).strip().lower() in MINOR)
    c["no severe confusion"] = not any(severe(x) for x in conf)
    req = t.get("required_fields", [])
    c["no required field unknown"] = all(a.get(k) and not str(a[k]).strip().lower().startswith("unknown") for k in req)
    return c


def load(path, what):
    try: return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as e: bad(f"{what} {path}: {type(e).__name__}")


if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    truth = load(sys.argv[1], "truth file"); readers = sys.argv[2:]
    if not isinstance(truth, dict): bad("the truth file must be a JSON object")
    unknown = set(truth) - GRADING_KEYS - OTHER_KEYS
    if unknown: bad(f"unknown truth keys {sorted(unknown)} (a misspelled key would silently grade nothing)")
    if not (set(truth) & GRADING_KEYS): bad(f"the truth file grades nothing: give at least one of {sorted(GRADING_KEYS)}")
    for k in GRADING_KEYS & set(truth):                           # a key that holds nothing grades nothing
        v = truth[k]
        if k == "min_sections": ok_ = isinstance(v, int) and not isinstance(v, bool) and v >= 1
        elif k == "steps_all_of": ok_ = isinstance(v, list) and v and all(isinstance(g, list) and g and all(isinstance(x, str) and x for x in g) for g in v)
        else: ok_ = isinstance(v, list) and v and all(isinstance(x, str) and x for x in v)
        if not ok_: bad(f"truth key '{k}' must be non-empty (a list of keywords, or a whole number >= 1 for min_sections): an empty requirement is always satisfied")
    if "result_keywords" in truth and not (isinstance(truth.get("result_min_hits", 2), int) and 1 <= truth.get("result_min_hits", 2) <= len(truth["result_keywords"])): bad("result_min_hits must be between 1 and the number of result_keywords")
    if len(readers) < 2: print("need at least two readers: one lucky reader proves little"); sys.exit(2)
    data, seen = [], {}
    for p in readers:
        a = load(p, "reader file")
        if not isinstance(a, dict): bad(f"reader file {p} must be a JSON object")
        key = hashlib.sha256(json.dumps(a, sort_keys=True).encode()).hexdigest()
        if key in seen: bad(f"{p} is identical to {seen[key]}: duplicate answers are one reader, not two")
        seen[key] = p; data.append((p, a))
    ok = True
    for p, a in data:
        res = grade(truth, a); print(p)
        for k, v in res.items(): print(f"  [{'PASS' if v else 'FAIL'}] {k}")
        ok &= all(res.values())
    print("COLD READ " + ("PASS" if ok else "FAIL")); sys.exit(0 if ok else 1)
