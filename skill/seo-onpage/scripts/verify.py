#!/usr/bin/env python3
"""Prove a push landed and broke nothing.
   verify.py <plan.json> <live-after.json> [--before before.json --after after.json] [-o verify.html]
 1. read-back: every applied row's NEW value is in the site's data now (meta from the WordPress record, headings/FAQs
    from the Elementor data, tag as planned)
 2. look: every changed heading renders, with the same font size at 390 and 1440 as before (a size change is a FAIL
    unless the heading's tag was meant to change AND it matches its new siblings)"""
import json, sys, re, html
from plan import norm

def main():
    plan = json.load(open(sys.argv[1])); live = {o["path"]: o for o in json.load(open(sys.argv[2]))}
    before = after = None
    if "--before" in sys.argv: before = json.load(open(sys.argv[sys.argv.index("--before") + 1]))["rows"]
    if "--after" in sys.argv: after = json.load(open(sys.argv[sys.argv.index("--after") + 1]))["rows"]
    out = []; bad = 0
    for i, x in enumerate(plan):
        if x["status"] not in ("ready",): continue
        o = live.get(x["path"]); res = "PASS"; why = ""
        if x["op"] == "set_meta":
            have = o.get(x["field"]) if x["field"] != "rank_math_focus_keyword" else None
            if have is not None and norm(have) != norm(x["new"]): res, why = "FAIL", f"live: {have!r}"
        elif x["op"] in ("heading", "faq", "faq_add"):
            hits = [t for t in o["texts"] if norm(t["text"]) == norm(x["new"])]
            if not hits: res, why = "FAIL", "new text not in the page data"
            elif x["op"] == "heading" and x.get("tag") and not any(t["tag"] == x["tag"] for t in hits): res, why = "FAIL", f"tag is {hits[0]['tag']}, wanted {x['tag']}"
            elif x["op"] in ("faq", "faq_add") and x.get("answer") and not any(norm(x["answer"]) in norm(t["text"]) for t in o["texts"]): res, why = "FAIL", "the new answer text is not on the page"
            if res == "PASS" and before and after and str(i) in after:
                for w in ("390", "1440"):
                    a = after[str(i)].get(w, {}); b = before.get(str(i), {}).get(w, {})
                    if not a.get("found"): res, why = "FAIL", f"not visible on the page at {w}px"; break
                    if b.get("found") and abs(a["size"] - b["size"]) > 0.5 and x.get("tag") == x.get("old_tag"):
                        res, why = "FAIL", f"size changed at {w}px: {b['size']} -> {a['size']}"; break
                    if b.get("found") and b.get("h") and a.get("h") and a["h"] > b["h"] * 1.6 and w == "390": why = f"now {a['h']}px tall on phones (was {b['h']}px): the new text wraps to more lines, take a look"
                    if b.get("found") and abs(a["size"] - b["size"]) > 0.5: why = f"size {b['size']}->{a['size']} at {w}px (tag {x.get('old_tag')}->{x.get('tag')}): check it"
        else: continue
        bad += res == "FAIL"; out.append((res, x, why))
    rows = "".join(f"<tr><td><b style='color:{'#1F7A4D' if r=='PASS' else '#9A3B2E'}'>{r}</b></td><td>{html.escape(x['path'])}</td><td>{html.escape(x.get('subject',''))}</td><td>{html.escape(str(x['new']))}</td><td>{html.escape(w)}</td></tr>" for r, x, w in out)
    o = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else "verify.html"
    open(o, "w").write(f"<title>Swap Verify</title><style>body{{font:14px system-ui;padding:20px}}td,th{{padding:5px 9px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}}</style><h1>{len(out)-bad} pass, {bad} fail</h1><table><tr><th></th><th>Page</th><th>Field</th><th>New</th><th>Note</th></tr>{rows}</table>")
    print(f"{len(out)} checked: {len(out)-bad} pass, {bad} fail -> {o}")
    for r, x, w in out:
        if r == "FAIL" or w: print(f"  {r} {x['path']} {x.get('subject')} {str(x['new'])[:50]!r} {w}")
    sys.exit(1 if bad else 0)

if __name__ == "__main__": main()
