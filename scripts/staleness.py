#!/usr/bin/env python3
"""A judgement older than the artifact is not a pass.
usage: staleness.py judgement.json artifact [--stamp]
  --stamp  record the artifact's content hash in the judgement file (do this when the judgement is made)
  check    exit 0 fresh | 1 STALE | 2 bad usage | 3 cannot establish freshness (never a pass)
If the judgement holds a stamped hash, content is compared (files and whole directory trees). Otherwise only modification times are compared:
that is weaker (touch renews it, a git checkout resets it), and the output says so."""
import hashlib, json, os, sys

def tree_hash(path):
    h = hashlib.sha256()
    if os.path.isfile(path):
        h.update(open(path, "rb").read()); return h.hexdigest()
    for d, dirs, files in os.walk(path):
        dirs[:] = sorted(x for x in dirs if x not in (".git", "node_modules"))
        for f in sorted(files):
            p = os.path.join(d, f); h.update(os.path.relpath(p, path).encode()); h.update(b"\0"); h.update(open(p, "rb").read())
    return h.hexdigest()

args = [x for x in sys.argv[1:] if x != "--stamp"]; stamp = "--stamp" in sys.argv[1:]
if len(args) != 2: print(__doc__); sys.exit(2)
j, a = args
if not (os.path.exists(j) and os.path.exists(a)): print("missing file - cannot establish freshness"); sys.exit(3)
try: jd = json.load(open(j, encoding="utf-8"))
except (OSError, ValueError): jd = None
if stamp:
    if not isinstance(jd, dict): print("the judgement must be a JSON object to be stamped"); sys.exit(2)
    jd["artifact_sha256"] = tree_hash(a); json.dump(jd, open(j, "w"), indent=1); print("stamped"); sys.exit(0)
if isinstance(jd, dict) and jd.get("artifact_sha256"):
    if jd["artifact_sha256"] != tree_hash(a): print("STALE: the artifact's content changed after the judgement - re-review required"); sys.exit(1)
    print("fresh (content hash matches)"); sys.exit(0)
if os.path.getmtime(a) > os.path.getmtime(j):
    print("STALE: artifact changed after the judgement - re-review required"); sys.exit(1)
print("fresh by modification time only (weak: run with --stamp when you judge to compare content instead)"); sys.exit(0)
