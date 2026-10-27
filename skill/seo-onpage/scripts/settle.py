#!/usr/bin/env python3
"""After a push + purge: fetch every changed page as a phone and as a desktop browser until the cached copy carries
the new text (each cache layer keeps its own phone + desktop copy). Reports pages still stale after the timeout.
   settle.py <plan.json> <base-url> [timeout-seconds]"""
import json, sys, time, subprocess, re
from plan import norm
plan = json.load(open(sys.argv[1])); base = sys.argv[2].rstrip("/"); limit = int(sys.argv[3]) if len(sys.argv) > 3 else 180
UA = {"desktop": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/130 Safari/537.36",
      "phone": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"}
want = {}
for x in plan:
    if x.get("status") == "ready" and x.get("op") in ("heading", "faq", "faq_add"): want.setdefault(x["path"], []).append(norm(x["new"]))
left = {(p, d) for p in want for d in UA}; t0 = time.time()
while left and time.time() - t0 < limit:
    for p, d in sorted(left):
        h = subprocess.run(["curl", "-sL", "--max-time", "25", "-A", UA[d], base + p], capture_output=True, text=True).stdout
        txt = norm(re.sub(r"<[^>]+>", " ", h))
        if all(w in txt for w in want[p]): left.discard((p, d))
    if left: time.sleep(10)
print(f"settled {len(want)*2 - len(left)}/{len(want)*2} page copies" + (f"; STALE: {sorted(left)}" if left else ""))
sys.exit(1 if left else 0)
