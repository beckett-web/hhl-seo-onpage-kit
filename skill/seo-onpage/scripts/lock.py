#!/usr/bin/env python3
"""Pin the size of every heading whose tag the plan changes, to what it measures NOW (snapshot before).
   lock.py <plan.json> <before.json>   (rewrites plan.json in place, adds "lock": {"390": px, "1440": px})
apply.php turns a lock into the widget's own CSS, so SEO tag changes never change how the page looks."""
import json, sys
plan = json.load(open(sys.argv[1])); before = json.load(open(sys.argv[2]))["rows"]; n = 0
for i, x in enumerate(plan):
    if x.get("op") == "heading" and x.get("tag") and x.get("old_tag") and x["tag"] != x["old_tag"]:
        b = before.get(str(i), {})
        if b.get("390", {}).get("found") and b.get("1440", {}).get("found"):
            x["lock"] = {"390": b["390"]["size"], "1440": b["1440"]["size"]}; n += 1
        else: x["why"] = (x.get("why", "") + "; size not measured, tag change may change the size").strip("; ")
json.dump(plan, open(sys.argv[1], "w"), indent=1, ensure_ascii=False); print(f"{n} tag changes size-locked")
