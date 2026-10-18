import json, os, subprocess, sys, tempfile, time
here = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(here, "..", "scripts")
d = tempfile.mkdtemp(); ok = True
def w(n, o): p = os.path.join(d, n); json.dump(o, open(p, "w")); return p
def run(*a): return subprocess.run([sys.executable, *a], capture_output=True, text=True).returncode
def expect(name, got, want):
    global ok; g = got == want; ok &= g; print(("ok   " if g else "FAIL ") + f"{name}: exit {got} (want {want})")

truth = w("truth.json", {"claim_any": ["receipt"], "steps_all_of": [["copy"], ["paste"], ["send"]], "result_keywords": ["table", "total", "category"],
                         "result_min_hits": 2, "min_sections": 4, "required_fields": ["summary", "claim_seen", "result_seen"]})
good = {"summary": "turn receipts into a sheet", "claim_seen": "receipt photos become a table", "steps": ["copy prompt", "paste it", "send"],
        "result_seen": "a table with total per category", "sections": ["a", "b", "c", "d"], "confusions": [{"text": "x", "severity": "minor"}]}
sev = dict(good, confusions=[{"text": "cannot follow", "severity": "severe"}])
unk = dict(good, result_seen="unknown")
good2 = dict(good, summary="photos of receipts become a spreadsheet", steps=["copy the prompt", "paste it into the chat", "send it"])
expect("two good readers pass", run(os.path.join(S, "grade.py"), truth, w("a.json", good), w("b.json", good2)), 0)
expect("severe confusion fails", run(os.path.join(S, "grade.py"), truth, w("a.json", good), w("c.json", sev)), 1)
expect("unknown required field fails", run(os.path.join(S, "grade.py"), truth, w("a.json", good), w("u.json", unk)), 1)
expect("single reader refused", run(os.path.join(S, "grade.py"), truth, w("a.json", good)), 2)
expect("unparseable reader fails", run(os.path.join(S, "grade.py"), truth, w("a.json", good), w("p.json", {"parse_error": "x"})), 1)
j = w("judge.json", {"pass": True}); art = os.path.join(d, "v.mp4"); open(art, "w").write("x")
os.utime(j, (time.time() - 100, time.time() - 100))
expect("artifact newer than judgement => stale", run(os.path.join(S, "staleness.py"), j, art), 1)
os.utime(art, (time.time() - 200, time.time() - 200))
expect("judgement newer than artifact => fresh", run(os.path.join(S, "staleness.py"), j, art), 0)
# --- review findings: every one of these used to pass or crash
def out(*a): r = subprocess.run([sys.executable, *a], capture_output=True, text=True); return r.returncode, r.stdout
G = os.path.join(S, "grade.py")
for label, sev in (("capitalised Severe", "Severe"), ("critical", "critical"), ("missing severity", None)):
    c = dict(good, confusions=[{"text": "lost"} if sev is None else {"text": "lost", "severity": sev}])
    rc, o = out(G, truth, w("a.json", good), w("sv.json", c)); expect(f"{label} counts as a severe confusion", (rc, "[FAIL] no severe confusion" in o), (1, True))
rc, o = out(G, truth, w("a.json", good), w("str.json", dict(good, confusions=["I was lost"]))); expect("a bare-string confusion fails closed, no crash", (rc, "Traceback" in o), (1, False))
e = w("e.json", {}); rc, o = out(G, e, w("e1.json", {}), w("e2.json", {"x": 1})); expect("an empty truth file grades nothing => exit 2", rc, 2)
rc, o = out(G, w("typo.json", {"claim_anyy": ["x"]}), w("a.json", good), w("b2.json", dict(good, summary="other"))); expect("a misspelled truth key is exit 2", rc, 2)
rc, o = out(G, truth, w("a.json", good), w("a_copy.json", good)); expect("the same answers twice are not two readers => exit 2", rc, 2)
rc, o = out(G, truth, w("a.json", good), os.path.join(d, "nope.json")); expect("a missing reader file is exit 2, not a traceback", (rc, "Traceback" in o), (2, False))
rc, o = out(G, truth, w("a.json", good), w("lst.json", [1, 2])); expect("a reader that is a JSON list is exit 2", rc, 2)
rc, o = out(G, truth, w("a.json", good), w("blank.json", dict(good, sections=["", "", "", ""], summary="Receipts to sheet again"))); expect("blank sections do not count as structure", (rc, "[FAIL] structure recovered" in o), (1, True))
art = os.path.join(d, "dir-artifact"); os.makedirs(art); open(os.path.join(art, "x.txt"), "w").write("v1")
jj = w("j2.json", {"pass": True}); rc, o = out(os.path.join(S, "staleness.py"), jj, art, "--stamp"); expect("stamp the judgement", rc, 0)
rc, o = out(os.path.join(S, "staleness.py"), jj, art); expect("stamped judgement is fresh while content is unchanged", rc, 0)
open(os.path.join(art, "x.txt"), "w").write("v2"); os.utime(jj, (time.time() + 100, time.time() + 100))
rc, o = out(os.path.join(S, "staleness.py"), jj, art); expect("a nested file change makes a stamped judgement STALE even if the judgement is newer", rc, 1)
for label, tr_ in (("claim_all []", {"claim_all": []}), ("min_sections 0", {"min_sections": 0}), ("result_min_hits 0", {"result_keywords": ["x"], "result_min_hits": 0}), ("min_sections as a string", {"claim_any": ["x"], "min_sections": "4"})):
    rc, o = out(G, w("tx.json", tr_), w("ra.json", {"summary": "a"}), w("rb.json", {"summary": "b"})); expect(f"an empty requirement grades nothing: {label} => exit 2", (rc, "Traceback" in o), (2, False))
sys.exit(0 if ok else 1)

