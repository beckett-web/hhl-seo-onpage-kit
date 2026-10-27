#!/usr/bin/env python3
"""seo audit <site>: map every page of a site section by section, so you can talk about it in plain words.
Writes ~/.seo-onpage/sites/<site>/
  SECTION-MAP.html   every page -> its sections in order: name, type, headings, a screenshot of each section
  section-map.json   the same as data (what the skill reads when you say "the FAQ on florida interior")
  onpage-doc.html    a ready-to-paste on-page doc: one table per page, Current filled from the live site,
                     Suggested empty. Copy everything, paste into a Google Doc, write the Suggested column, then
                     `seo plan <site> <doc-link>` matches every row exactly.
Read-only. Run it when you start a client and after any big change."""
import json, os, re, sys, subprocess, html
from urllib.parse import urlparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo
from plan import norm

TYPES = [("FAQ", r"(faq|frequently asked|questions)"), ("Reviews", r"(review|testimonial|what .* say|clients say)"),
 ("Process / steps", r"(process|how it works|steps?|1-2-3|simple as)"), ("Why us", r"(why (choose|homeowners|us|.*choose)|difference|promise)"),
 ("Service areas", r"(serving|service areas?|areas we|where we paint|pick your city|neighborhood)"), ("Projects / gallery", r"(project|gallery|our work|portfolio|recent)"),
 ("Call to action", r"(let'?s get you a number|get (a|your) free|ready to|thinking about|planning a|contact|request)"), ("Team / about", r"(team|about|meet|our crew|people|story|since \d{4})"),
 ("Warranty / offer", r"(warrant|free design|offer|special)"), ("Careers", r"(career|apply|join|hiring|jobs)"),
 ("Services", r"(services?|painting|staining|cabinet|commercial|interior|exterior)")]
def kind(heads, first):
    t = " ".join(heads).lower()
    if first: return "Hero"
    for k, rx in TYPES:
        if re.search(rx, t): return k
    return "Other"

def main(key):
    s = seo.site(key); out = os.path.join(seo.CONF, "sites", key); os.makedirs(out, exist_ok=True)
    raw = seo.wp(s, "eval 'foreach(get_posts([\"post_type\"=>[\"page\",\"post\",\"project\"],\"post_status\"=>\"publish\",\"numberposts\"=>-1]) as $p) echo wp_parse_url(get_permalink($p),PHP_URL_PATH),\"\\n\";'", env="READONLY=1")
    paths = sorted({l.strip() for l in raw.splitlines() if l.startswith("/")}, key=lambda p: (p.count("/"), p))
    from plan import redirects
    gone = redirects(s["base"], paths); paths = [p for p in paths if p not in gone]   # a page that redirects is never seen: leave it out
    live = seo.locate(s, paths, os.path.join(out, "live.json"))
    pages = []
    for o in live:
        secs = []; order = []
        for t in o["texts"]:
            k = (t["source"], t["section"])
            if k not in order: order.append(k)
        for n, k in enumerate(order):
            ts = [t for t in o["texts"] if (t["source"], t["section"]) == k]
            heads = [f"{t['tag']}: {t['text']}" for t in ts if t["tag"] and t["tag"].startswith("h")]
            secs.append({"n": n + 1, "id": k[1], "source": k[0], "type": kind([h.split(': ', 1)[1] for h in heads], n == 0 and k[0] == "page"),
                         "name": next((h.split(": ", 1)[1] for tg in ("h1", "h2", "h3") for h in heads if h.startswith(tg + ":")), heads[0].split(": ", 1)[1] if heads else (ts[0]["text"][:60] if ts else "")), "headings": heads,
                         "faq": [t["text"] for t in ts if t["tag"] == "summary"], "shared": k[0] != "page"})
        pages.append({"path": o["path"], "post": o["post"], "title": o.get("title"), "seo_title": o.get("rank_math_title"),
                      "seo_desc": o.get("rank_math_description"), "sections": secs})
    json.dump(pages, open(os.path.join(out, "section-map.json"), "w"), indent=1, ensure_ascii=False)
    shots = os.path.join(out, "shots"); os.makedirs(shots, exist_ok=True)
    subprocess.run(["node", os.path.join(seo.HERE, "shoot_sections.cjs"), os.path.join(out, "section-map.json"), s["base"], shots], check=False)
    e = html.escape
    body = []
    for p in pages:
        body.append(f"<h2 id='{e(p['path'])}'>{e(p['path'])} <small>{e(p['title'] or '')}</small></h2><div class=g>")
        for x in p["sections"]:
            img = f"shots/{re.sub(r'[^a-z0-9]+', '-', p['path']).strip('-') or 'home'}-{x['n']}.jpg"
            body.append(f"<div class=c><img loading=lazy src='{img}' alt=''><b>{x['n']}. {e(x['type'])}</b> {('<span class=sh>shared on several pages</span>' if x['shared'] else '')}"
                        f"<div class=nm>{e(x['name'])}</div><ul>{''.join(f'<li>{e(h)}</li>' for h in x['headings'][:8])}</ul></div>")
        body.append("</div>")
    open(os.path.join(out, "SECTION-MAP.html"), "w").write(f"""<title>{e(key)} Section Map</title><meta name=viewport content="width=device-width"><style>
body{{font:13px/1.45 system-ui;margin:0;padding:20px max(16px,env(safe-area-inset-left,0px));background:#F6F7FA;color:#14213A}} h2{{margin:28px 0 8px;font-size:16px}} small{{color:#5B6578;font-weight:400}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}} .c{{background:#fff;border:1px solid #DDE3EC;border-radius:8px;padding:8px}}
.c img{{width:100%;height:130px;object-fit:cover;object-position:top;border-radius:4px;background:#EEF2F8}} .nm{{color:#1E4FD8;margin:2px 0}} ul{{margin:4px 0 0;padding-left:16px;color:#5B6578}} .sh{{background:#FBF0DE;color:#9A5B00;border-radius:9px;padding:1px 6px;font-size:11px}}</style>
<h1>{e(key)}: every page, section by section</h1><p>{len(pages)} pages. Say "section 4 on /florida/interior-painting/" or "the FAQ on florida interior" and the skill knows which block you mean.</p>{''.join(body)}""")
    doc = []
    for i, p in enumerate(pages, 1):
        rows = [("Meta Title", p["seo_title"] or ""), ("Target KWs", ""), ("Meta Description", p["seo_desc"] or "")]
        for x in p["sections"]:
            if x["shared"]: continue
            for h in x["headings"]:
                tag, txt = h.split(": ", 1)
                if tag in ("h1", "h2"): rows.append((tag.upper(), txt))
            for q in x["faq"]: rows.append(("FAQ", q))
        doc.append(f"<p><b>{i}. {e(p['title'] or p['path'])}</b></p><p>{e(s['base'].rstrip('/') + p['path'])}</p><table border=1 cellpadding=4><tr><td>Subject</td><td>Current</td><td>Suggested</td><td>Comment</td></tr>"
                   + "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td></td><td></td></tr>" for a, b in rows) + "</table><p></p>")
    open(os.path.join(out, "onpage-doc.html"), "w").write("<meta charset=utf-8><h1>On-page doc: " + e(key) + "</h1><p>Write only the Suggested column. Leave a row's Suggested empty to keep it. Use &lt;H2&gt;...&lt;/H2&gt; to change a tag. New FAQ: a FAQ row with Current empty and 'Question? (Answer: ...)'.</p>" + "".join(doc))
    print(f"{len(pages)} pages mapped -> {out}/SECTION-MAP.html, section-map.json, onpage-doc.html")

if __name__ == "__main__": main(sys.argv[1])
