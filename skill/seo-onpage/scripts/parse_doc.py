#!/usr/bin/env python3
"""Tamim's on-page doc (Google Doc, "Subject | Current | Suggested | Comment" tables, one per page) -> doc.json.
   parse_doc.py <google-doc-url-or-id | local .html> [-o doc.json]
The doc only has to be link-readable. Each table must sit under its page title + URL, as in the Elevation doc."""
import json, re, sys, html, urllib.request, urllib.error
from bs4 import BeautifulSoup

def fetch(src):
    if src.endswith(".html") and not src.startswith("http"): return open(src, encoding="utf-8").read()
    m = re.search(r"/d/([A-Za-z0-9_-]{20,})", src); did = m.group(1) if m else src
    u = f"https://docs.google.com/document/d/{did}/export?format=html"
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
            return r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        sys.exit("can't open that doc (" + str(e.code) + "): check the link, and Share → General access → Anyone with the link → Viewer"
                 if e.code in (401, 403, 404) else f"Google Docs answered {e.code}: try again in a minute")

def clean(t): return re.sub(r"\s+", " ", html.unescape(t.replace("\xa0", " "))).strip()
KEEP = re.compile(r"^(keep( as is)?|no change|same|—|-|n/?a)\.?$", re.I)
TAG = re.compile(r"^\s*<\s*(h[1-6]|p)\s*>(.*?)<\s*/\s*\1\s*>\s*$", re.I | re.S)

def parse_suggested(subject, cur, sug):
    if re.match(r"^\s*[-—–]?\s*$", cur or ""): cur = None
    r = {"subject": subject, "current": cur, "suggested": sug}
    if KEEP.match(sug) or not sug: r["action"] = "keep"; return r
    if subject.upper() == "FAQ":
        m = re.match(r"(.*?)\(\s*Answer:\s*(.*)\)\s*$", sug, re.S)
        r.update(action="faq", question=clean(m.group(1)) if m else clean(sug), answer=clean(m.group(2)) if m else None)
        return r
    m = TAG.match(sug)
    if m: r.update(action="heading", tag=m.group(1).lower(), text=clean(re.sub(r"<[^>]+>", "", m.group(2))))
    elif re.match(r"^\s*<\s*(h[1-6]|p)\s*>", sug, re.I):   # opening tag only, stray closing tag elsewhere
        t = re.match(r"^\s*<\s*(h[1-6]|p)\s*>", sug, re.I).group(1).lower(); r.update(action="heading", tag=t, text=clean(re.sub(r"<[^>]+>", "", sug)))
    elif subject.upper() in ("META TITLE", "META DESCRIPTION", "TARGET KWS"): r.update(action=subject.lower().replace(" ", "_"), text=clean(sug))
    elif re.match(r"^(H[1-6]|HEADING)$", subject, re.I): r.update(action="heading", tag=subject.lower() if subject.upper() != "HEADING" else None, text=clean(sug))
    else: r.update(action="other", text=clean(sug))
    return r

def parse(doc_html):
    s = BeautifulSoup(doc_html, "html.parser"); pages = []
    for tab in s.find_all("table"):
        rows = [[clean(td.get_text("\n", strip=True)) for td in tr.find_all(["td", "th"])] for tr in tab.find_all("tr")]
        if not rows or rows[0][:2] != ["Subject", "Current"]: continue
        url = title = None; x = tab
        for _ in range(12):
            x = x.find_previous(["p", "h1", "h2", "h3", "h4"])
            if x is None: break
            t = clean(x.get_text(" ", strip=True))
            if not url and re.match(r"^https?://\S+$", t): url = t; continue
            if url and re.match(r"^\d+\.\s+\S", t) and ";" not in t: title = re.sub(r"^\d+\.\s+", "", t); break
        out = []
        for r in rows[1:]:
            if len(r) < 3 or not r[0]: continue
            out.append(parse_suggested(r[0], r[1], r[2]) | {"comment": r[3] if len(r) > 3 else ""})
        # loose FAQ lines right after the table, before the next page title ("FAQ" heading then questions)
        extra = []; y = tab
        while True:
            y = y.find_next(["p", "h1", "h2", "h3", "h4", "table"])
            if y is None or y.name == "table": break
            if y.find_parent("table") is not None: continue
            t = clean(y.get_text(" ", strip=True))
            if re.match(r"^\d+\.\s+\S", t) and ";" not in t: break
            if t and t.upper() != "FAQ": extra.append(t)
        pages.append({"title": title, "url": url, "rows": out, "after_table": extra})
    return pages

if __name__ == "__main__":
    src = sys.argv[1]; o = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else "doc.json"
    raw = fetch(src)
    if "accounts.google.com" in raw[:5000] or "ServiceLogin" in raw[:5000]: sys.exit("the doc isn't shared: Share → General access → Anyone with the link → Viewer, then run again")
    pages = parse(raw)
    if not pages: sys.exit("no on-page tables found: each page needs a table starting with 'Subject | Current | Suggested | Comment' under its title + URL")
    json.dump(pages, open(o, "w"), indent=1, ensure_ascii=False)
    acts = {}
    for p in pages:
        for r in p["rows"]: acts[r["action"]] = acts.get(r["action"], 0) + 1
    print(f"{len(pages)} pages -> {o}  rows by action: {acts}  pages without URL: {[p['title'] for p in pages if not p['url']]}")
