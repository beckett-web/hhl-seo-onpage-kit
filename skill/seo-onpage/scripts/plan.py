#!/usr/bin/env python3
"""doc.json (parse_doc.py) + live.json (locate.php, read-only) -> plan.json + plan.html (NOW vs NEW, one row per change).
   plan.py <doc.json> <live.json> [-o <dir>]
Nothing is written to the site here. Every row gets a status:
  ready      exact element found on the page itself, safe to apply
  global     the text lives in a shared template: changing it changes every page that uses it -> needs an explicit OK
  fuzzy      only a near match was found -> check it before applying
  not_found  the doc's "Current" text is not on the live page (doc out of date, or it is in an image/plugin) -> skipped
  blocked    the change is outside on-page scope (e.g. a tag the element type can't take) -> skipped, with the reason
  keep       "Keep as is" -> nothing to do (we still confirm the text exists)"""
import json, re, sys, html, difflib, os
from urllib.parse import urlparse

def norm(t):
    t = html.unescape(t or "").lower().replace("&", " and ").replace("+", " and ")
    t = re.sub(r"[’'`]", "", t); t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()

TAGGABLE = {"heading": "header_size", "icon-box": "title_size", "image-box": "title_size", "call-to-action": "title_tag", "flip-box": "title_tag"}

def find(texts, current, prefer_tags=None):
    """best element for the doc's 'current' text: exact normalized match first (page before template), then fuzzy"""
    n = norm(current); hits = [t for t in texts if norm(t["text"]) == n]
    if prefer_tags: hits.sort(key=lambda t: (t["tag"] not in prefer_tags))
    hits.sort(key=lambda t: t["source"] != "page")
    if hits: return hits[0], "exact", hits
    best, score = None, 0
    for t in texts:
        r = difflib.SequenceMatcher(None, n, norm(t["text"])).ratio()
        if r > score: best, score = t, r
    return (best, "fuzzy", [best]) if score >= 0.82 else (None, "none", [])

def faq_accordion(texts):
    """the page's FAQ accordion: the accordion element in a section whose heading says FAQ/Questions (page first)"""
    accs = {}
    for t in texts:
        if t["widget"] in ("nested-accordion", "n-accordion", "accordion", "toggle"): accs.setdefault((t["post"], t["el"]), t)
    faq_sections = {t["section"] for t in texts if t["tag"] and t["tag"].startswith("h") and re.search(r"faq|question", t["text"], re.I)}
    c = [a for a in accs.values() if a["section"] in faq_sections]
    c.sort(key=lambda a: a["source"] != "page")
    return c[0] if c else None

STOP = set("in the and of for a to our your with at on from by is are what how".split())
def suggest(texts, new, tag):
    """live headings ranked by shared keywords with the new text: same tag first"""
    want = {w for w in norm(new).split() if w not in STOP}; out = []
    for t in texts:
        if not t["tag"] or not t["tag"].startswith("h") or t["widget"] == "post": continue
        have = {w for w in norm(t["text"]).split() if w not in STOP}
        if not have: continue
        s = len(want & have) / max(1, len(have)) + (0.25 if t["tag"] == tag else 0) + (0.1 if t["source"] == "page" else 0)
        out.append((s, t))
    out.sort(key=lambda x: -x[0])
    return [{"el": t["el"], "post": t["post"], "tag": t["tag"], "text": t["text"], "source": t["source"], "score": round(s, 2)} for s, t in out[:3]]

def is_global(el, users, path):
    """text in a template counts as global unless that template renders only this one page (an archive template)"""
    return el["source"] != "page" and users.get(el["post"], {path}) != {path}

def template_users(live):
    u = {}
    for o in live:
        for t in o.get("includes", []): u.setdefault(t, set()).add(o["path"])
    return u

def redirects(base, paths):
    """paths that answer with a redirect on the live site -> where they go (editing them changes nothing visible)"""
    import subprocess; out = {}
    for path in paths:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code} %{redirect_url}", "--max-time", "20", base.rstrip("/") + path], capture_output=True, text=True).stdout.split()
        if r and r[0] in ("301", "302", "307", "308") and len(r) > 1:
            to = urlparse(r[1]).path or "/"
            if to.rstrip("/") != path.rstrip("/"): out[path] = to
    return out

def plan(doc, live, base=None):
    by_path = {o["path"]: o for o in live}; users = template_users(live); ops = []; owner = {}
    redir = redirects(base, [urlparse(p["url"] or "").path or "/" for p in doc]) if base else {}
    for p in doc:
        path = urlparse(p["url"] or "").path or "/"; o = by_path.get(path)
        if not o: ops.append({"page": p["title"], "path": path, "status": "not_found", "why": "URL not located on the site"}); continue
        if path in redir:
            for r in p["rows"]:
                ops.append({"page": p["title"], "path": path, "subject": r["subject"], "new": r.get("text") or r.get("question"), "status": "blocked",
                            "why": f"{path} redirects to {redir[path]}: nobody sees this page. Put these rows on {redir[path]} instead"})
            continue
        if o.get("post") and o["post"] in owner:
            ops.append({"page": p["title"], "path": path, "status": "blocked", "subject": "page",
                        "why": f"same WordPress page as '{owner[o['post']]}' (this URL redirects there): merge the two sections in the doc"}); continue
        if o.get("post"): owner[o["post"]] = p["title"]
        texts = o["texts"]; meta_target = ({"kind": "option", "keys": o.get("meta_option")} if o.get("kind") == "post_type_archive"
                                           else {"kind": "post", "post": o["post"]})
        for r in p["rows"]:
            base = {"page": p["title"], "path": path, "subject": r["subject"], "now": r.get("current"), "comment": r.get("comment", "")}
            a = r["action"]
            if a in ("meta_title", "meta_description"):
                key = "rank_math_title" if a == "meta_title" else "rank_math_description"
                live_now = o.get(key) or ""
                ops.append(base | {"op": "set_meta", "target": meta_target, "field": key, "new": r["text"], "live_now": live_now,
                                   "status": "ready" if o.get("post") or o.get("kind") == "post_type_archive" else "not_found",
                                   "why": "" if (not r.get("current") or norm(r["current"]) == norm(live_now)) else "live value differs from the doc's Current (fine: we write the Suggested)"})
                continue
            if a == "target_kws":
                kws = [re.sub(r"^\d+\.\s*", "", k.strip(" ;")) for k in re.split(r";|\n", r["text"]) if k.strip(" ;")]
                ops.append(base | {"op": "set_meta", "target": meta_target, "field": "rank_math_focus_keyword", "new": ",".join(kws), "now": None,
                                   "status": "ready" if o.get("post") else "blocked", "why": "" if o.get("post") else "archives have no focus keyword field"})
                continue
            if a == "keep":
                el, how, _ = find(texts, r.get("current") or "")
                ops.append(base | {"op": "none", "new": r.get("current"), "status": "keep", "why": "" if el else "note: the Current text was not found on the live page"})
                continue
            if a == "faq":
                el, how, _ = find(texts, r.get("current") or "", prefer_tags=["summary"]) if r.get("current") else (None, "none", [])
                if not el:
                    acc = faq_accordion(texts)
                    if r.get("current"): ops.append(base | {"op": "faq", "new": r["question"], "answer": r.get("answer"), "status": "not_found", "why": "question not on the page"})
                    elif not acc: ops.append(base | {"op": "faq_add", "new": r["question"], "answer": r.get("answer"), "status": "blocked", "why": "this page has no FAQ section to add to (adding one = new section, ask Beckett)"})
                    elif not r.get("answer"): ops.append(base | {"op": "faq_add", "new": r["question"], "status": "blocked", "why": "new FAQ needs an answer: write it as 'Question? (Answer: ...)'"})
                    else: ops.append(base | {"op": "faq_add", "post": acc["post"], "el": acc["el"], "widget": acc["widget"], "source": acc["source"], "now": None,
                                            "new": r["question"], "answer": r.get("answer"), "status": "global" if is_global(acc, users, path) else "ready",
                                            "why": "adds a new question to the page's FAQ"})
                    continue
                ops.append(base | {"op": "faq", "post": el["post"], "el": el["el"], "widget": el["widget"], "field": el["field"], "index": el.get("faq_index"),
                                   "now": el["text"], "new": r["question"], "answer": r.get("answer"), "source": el["source"],
                                   "status": "global" if is_global(el, users, path) else ("fuzzy" if how == "fuzzy" else "ready"),
                                   "why": f"in shared template, used on {len(users.get(el['post'], []))} pages" if is_global(el, users, path) else ""})
                continue
            if a == "heading":
                cur = r.get("current"); picks = None
                el, how, allhits = find(texts, cur or "", prefer_tags=["h1", "h2", "h3", "h4", "h5", "h6"]) if cur else (None, "none", [])
                if not el and not cur and (r.get("tag") == "h1" or r["subject"].upper() == "H1"):
                    h1s = [t for t in texts if t["tag"] == "h1" and t["source"] == "page"] or [t for t in texts if t["tag"] == "h1"]
                    if len(h1s) == 1: el, how, allhits = h1s[0], "h1", h1s
                if not el and not cur:
                    picks = suggest(texts, r["text"], r.get("tag") or r["subject"].lower())
                    ops.append(base | {"op": "heading", "new": r["text"], "tag": r.get("tag"), "status": "pick", "options": picks,
                                       "why": "doc has no Current: pick which live heading this replaces (closest first), or it's a new heading (ask Beckett)"}); continue
                if not el:
                    ops.append(base | {"op": "heading", "new": r["text"], "tag": r.get("tag"), "status": "not_found",
                                       "why": "no Current given: a NEW heading means a new element (ask Beckett)" if not cur else "Current text not on the live page"}); continue
                new_tag = r.get("tag"); old_tag = el["tag"]; status = "ready"; why = []
                if is_global(el, users, path): status = "global"; why.append(f"in shared template {el['source']}, used on {len(users.get(el['post'], []))} pages")
                if how == "fuzzy": status = "fuzzy" if status == "ready" else status; why.append(f"near match: live text is \"{el['text']}\"")
                if new_tag and new_tag != old_tag:
                    if el["widget"] in TAGGABLE or el.get("inline") or el["widget"] == "post": why.append(f"tag {old_tag} -> {new_tag}")
                    else: why.append(f"tag stays {old_tag}: a {el['widget']} title can't be {new_tag} (text still changes)"); new_tag = old_tag
                if len(allhits) > 1: why.append(f"{len(allhits)} identical texts on this page; changing the first in page order")
                ops.append(base | {"op": "heading", "post": el["post"], "el": el["el"], "widget": el["widget"], "field": el["field"],
                                   "inline": bool(el.get("inline")), "now": el["text"], "old_tag": old_tag, "tag": new_tag or old_tag,
                                   "new": r["text"], "source": el["source"], "status": status, "why": "; ".join(why)})
                continue
            ops.append(base | {"op": a, "new": r.get("text"), "status": "blocked", "why": f"'{r['subject']}' rows aren't handled yet"})
    return ops

CH = {"ready": "#1F7A4D", "global": "#9A5B00", "fuzzy": "#9A5B00", "pick": "#1E4FD8", "not_found": "#9A3B2E", "blocked": "#9A3B2E", "keep": "#5B6578"}
UK = re.compile(r"\b(colour|colours|coloured|neighbour\w*|centre\w*|favour\w*|honour\w*|behaviour|organis\w*|metres?|grey|moulding)\b", re.I)
def lint(ops):
    """house language rules on every NEW text (R051): no em dashes, US spelling"""
    for x in ops:
        t = " ".join(str(x.get(k) or "") for k in ("new", "answer"))
        notes = []
        if "—" in t or "–" in t: notes.append("has an em/en dash: use a comma or period")
        m = UK.findall(t)
        if m: notes.append("British spelling: " + ", ".join(sorted(set(w.lower() for w in m))))
        if x.get("field") == "rank_math_title" and len(x.get("new") or "") > 60: notes.append(f"title is {len(x['new'])} characters: Google cuts it near 60")
        if x.get("field") == "rank_math_description" and len(x.get("new") or "") > 160: notes.append(f"description is {len(x['new'])} characters: Google cuts it near 155-160")
        if x.get("field") == "rank_math_title" and "%" in (x.get("live_now") or ""): notes.append("the live title uses Rank Math variables (%sep%, %sitename%): yours replaces them with fixed text")
        if x.get("op") == "heading" and x.get("widget") == "post": notes.append("this is the post's title: it also changes its card title everywhere the post is listed (projects grid, related posts)")
        if notes and x["status"] == "ready" and any(k in " ".join(notes) for k in ("dash", "British")): x["status"] = "fuzzy"
        if notes: x["why"] = "; ".join([x.get("why", "")] + notes).strip("; ")
    return ops

def report(ops, out):
    for i, x in enumerate(ops): x["_i"] = i
    e = html.escape; pages = {}
    for x in ops: pages.setdefault((x["page"], x["path"]), []).append(x)
    cnt = {}
    for x in ops: cnt[x["status"]] = cnt.get(x["status"], 0) + 1
    rows = []
    for (pg, path), xs in pages.items():
        rows.append(f"<h2>{e(pg)} <small>{e(path)}</small></h2><div class=t><table><tr><th>Field</th><th>Now (live)</th><th>New</th><th>Status</th></tr>")
        for x in xs:
            tag = f"<code>{e(str(x.get('old_tag')))} → {e(str(x.get('tag')))}</code> " if x.get("tag") and x.get("old_tag") and x["tag"] != x["old_tag"] else (f"<code>{e(str(x.get('tag')))}</code> " if x.get("tag") else "")
            ans = f"<div class=a>A: {e(x['answer'])}</div>" if x.get("answer") else ""
            if x.get("options") and x["status"] == "pick": ans += "<div class=a>Replaces which? " + " · ".join(f"<b>{k}</b> <code>{e(o['tag'])}</code> {e(o['text'])}" for k, o in enumerate(x["options"], 1)) + f" &nbsp;→ <code>seo pick &lt;site&gt; {x['_i']} 1|2|3|new</code></div>"
            rows.append(f"<tr><td><b>#{x['_i']}</b> {e(x.get('subject',''))}</td><td>{e(str(x.get('now') or x.get('live_now') or '—'))}</td><td>{tag}{e(str(x.get('new') or ''))}{ans}</td>"
                        f"<td><b style='color:{CH[x['status']]}'>{x['status']}</b><div class=w>{e(x.get('why',''))}</div></td></tr>")
        rows.append("</table></div>")
    sumline = " · ".join(f"<b style='color:{CH[k]}'>{v} {k}</b>" for k, v in sorted(cnt.items()))
    page = f"""<title>SEO Swap Plan</title><meta name=viewport content="width=device-width"><style>
body{{font:14px/1.5 system-ui,sans-serif;margin:0;padding:24px max(16px,env(safe-area-inset-left,0px));background:#F6F7FA;color:#14213A}} h1{{margin:0 0 4px}} h2{{font-size:16px;margin:28px 0 6px}} small{{color:#5B6578;font-weight:400}}
.t{{overflow-x:auto;background:#fff;border:1px solid #DDE3EC;border-radius:8px}} table{{border-collapse:collapse;width:100%}} td,th{{padding:6px 10px;border-bottom:1px solid #EEF1F5;text-align:left;vertical-align:top}} th{{background:#EEF2F8;font-size:12px}}
code{{background:#E9EEFB;padding:1px 4px;border-radius:4px}} .w{{color:#5B6578;font-size:12px}} .a{{color:#5B6578;font-size:12px;margin-top:4px}}</style>
<h1>SEO swap plan</h1><p>{sumline}. Only <b>ready</b> rows (and <b>global</b> rows you OK) get applied. Nothing has changed on the site yet.</p>{''.join(rows)}"""
    open(os.path.join(out, "plan.html"), "w").write(page)

if __name__ == "__main__":
    if sys.argv[1] == "--report-only":   # re-draw plan.html from an existing plan.json (after lock.py)
        ops = json.load(open(sys.argv[2])); report(ops, sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else "."); sys.exit()
    doc, live = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
    out = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else "."
    base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else None
    ops = lint(plan(doc, live, base)); json.dump(ops, open(os.path.join(out, "plan.json"), "w"), indent=1, ensure_ascii=False); report(ops, out)
    c = {}
    for x in ops: c[x["status"]] = c.get(x["status"], 0) + 1
    print(f"{len(ops)} rows -> {out}/plan.json + plan.html  {c}")
