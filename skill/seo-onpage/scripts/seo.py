#!/usr/bin/env python3
"""seo: on-page SEO swaps from a Google Doc into a live WordPress + Elementor site, safely.

  seo sites                         list the sites you can reach (sites.json)
  seo access <site>                 test every connection for a site, say what's missing
  seo audit <site>                  section-by-section map of the site (names you can use: "fix the FAQ on florida interior")
  seo plan <site> <doc-url>         read the doc + the live site -> plan.html (NOW vs NEW per row). Writes nothing.
  seo push <site> [--globals]       apply the approved plan (ready rows; --globals adds shared-template rows), then
                                    purge caches, wait for every phone + desktop copy, read everything back, check sizes
  seo pick <site> <row> <1|2|3|new>  answer a "pick" row: which live heading it replaces (or new = skip it, ask Beckett)
  seo rollback <site> [<stamp>]     put the last (or a given) push back exactly as it was
  seo log "<what happened>"         add an issue to your issue log (feeds the rulebook)

Every write goes through the write guard with a scope file listing the exact pages; every run keeps its files in
runs/<site>/<stamp>/. Nothing touches a site without a plan you have seen."""
import json, os, sys, subprocess, time, shlex
from urllib.parse import urlparse
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.dirname(HERE)
HOME = os.path.expanduser("~"); CONF = os.environ.get("SEO_HOME", os.path.join(HOME, ".seo-onpage"))
RUNS = os.path.join(CONF, "runs")
_pw = os.path.join(HOME, ".seo-onpage", "node", "node_modules", "playwright")
if os.path.isdir(_pw): os.environ.setdefault("PLAYWRIGHT", _pw)
_keys = os.path.join(CONF, "keys.env")
if os.path.exists(_keys):
    for _l in open(_keys):
        _m = __import__("re").match(r'export (\w+)="(.*)"', _l.strip())
        if _m: os.environ.setdefault(_m.group(1), _m.group(2))

def sites():
    f = os.path.join(CONF, "sites.json")
    if not os.path.exists(f): sys.exit(f"no {f} yet: run onboarding (/seo-onpage → 'what do I do first?')")
    return json.load(open(f))

def site(key):
    s = sites().get(key)
    if not s: sys.exit(f"unknown site '{key}'. Known: {', '.join(sites())}")
    return s

def ssh(s, cmd, check=True, capture=True):
    """run a shell command in the site's WordPress folder over SSH"""
    path = s["wp_path"].replace("~", "$HOME", 1) if s["wp_path"].startswith("~") else s["wp_path"]
    full = f'cd "{path}" && {cmd}'
    args = ["ssh", "-i", os.path.expanduser(s["key"]), "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-p", str(s.get("port", 22)), f"{s['user']}@{s['host']}", full]
    r = subprocess.run(args, capture_output=capture, text=True)
    if check and r.returncode: sys.exit(f"ssh failed ({r.returncode}): {r.stderr.strip()[:400]}")
    return r.stdout

def wp(s, args, env=""):
    extra = " --skip-plugins=novamira" if s.get("hosting") == "ghl" else ""
    return ssh(s, f"{env} wp {args}{extra} 2>&1")

def upload(s, files, remote="seo-onpage"):
    ssh_dir = f"{s['user']}@{s['host']}:{remote}/"
    subprocess.run(["ssh", "-i", os.path.expanduser(s["key"]), "-p", str(s.get("port", 22)), f"{s['user']}@{s['host']}", f"mkdir -p ~/{remote} ~/hhl-scripts"], check=True)
    subprocess.run(["scp", "-q", "-i", os.path.expanduser(s["key"]), "-P", str(s.get("port", 22))] + files + [ssh_dir], check=True)

def run_dir(key, stamp=None, new=False):
    base = os.path.join(RUNS, key)
    if new: d = os.path.join(base, time.strftime("%Y%m%d-%H%M%S")); os.makedirs(d, exist_ok=True); return d
    if stamp: return os.path.join(base, stamp)
    runs = sorted(os.listdir(base)) if os.path.isdir(base) else []
    if not runs: sys.exit("no plan yet: run  seo plan <site> <doc-url>")
    return os.path.join(base, runs[-1])

def locate(s, paths, out):
    upload(s, [os.path.join(HERE, "locate.php")])
    raw = wp(s, "eval-file ~/seo-onpage/locate.php", env=f"READONLY=1 URLS={shlex.quote(','.join(paths))}")
    j = raw[raw.find("["):]; json.loads(j); open(out, "w").write(j); return json.loads(j)

def purge(s):
    """clear every cache layer this host has, in the order they serve"""
    for c in s.get("purge", []): ssh(s, c, check=False)
    wp(s, "cache flush", env="READONLY=1")

def hold(s, planf):
    """sites.json "hold": [{"paths": ["/", "/colorado/"], "until": "2026-12-01", "why": "..."}]: rows on held pages are blocked"""
    holds = [h for h in s.get("hold", []) if time.strftime("%Y-%m-%d") < h["until"]]
    if not holds: return
    plan = json.load(open(planf)); n = 0
    for x in plan:
        for h in holds:
            if any(x["path"] == p or (p != "/" and x["path"].startswith(p)) for p in h["paths"]) and x["status"] not in ("keep", "blocked"):
                x["status"] = "blocked"; x["why"] = f"page on hold until {h['until']}: {h.get('why', '')}".strip(": "); n += 1
    json.dump(plan, open(planf, "w"), indent=1, ensure_ascii=False); print(f"{n} rows blocked by holds")

def cmd_plan(key, doc):
    s = site(key); d = run_dir(key, new=True)
    py = sys.executable
    if subprocess.run([py, os.path.join(HERE, "parse_doc.py"), doc, "-o", f"{d}/doc.json"]).returncode: sys.exit(1)
    paths = [urlparse(p["url"] or "").path or "/" for p in json.load(open(f"{d}/doc.json"))]
    locate(s, paths, f"{d}/live.json")
    subprocess.run([py, os.path.join(HERE, "plan.py"), f"{d}/doc.json", f"{d}/live.json", "-o", d, "--base", s["base"]], check=True)
    hold(s, f"{d}/plan.json")
    subprocess.run(["node", os.path.join(HERE, "snapshot.cjs"), f"{d}/plan.json", s["base"], f"{d}/before.json", "before"], check=True)
    subprocess.run([py, os.path.join(HERE, "lock.py"), f"{d}/plan.json", f"{d}/before.json"], check=True)
    subprocess.run([py, os.path.join(HERE, "plan.py"), "--report-only", f"{d}/plan.json", "-o", d], check=False)
    print(f"\nplan: {d}/plan.html  (open it, check every row; nothing has changed on the site)")
    if not os.environ.get("SEO_NO_OPEN"): subprocess.run(["open", f"{d}/plan.html"], check=False)

def cmd_push(key, approve_globals=False, dry=False):
    s = site(key); d = run_dir(key); plan = json.load(open(f"{d}/plan.json"))
    if os.path.exists(f"{d}/backup.txt") and not dry:
        sys.exit("this plan was already pushed. Re-plan first (seo plan ...) so the backup and the checks match the site as it is now")
    posts = sorted({x["post"] for x in plan if x.get("post")} | {x["target"]["post"] for x in plan if x.get("target", {}).get("kind") == "post"})
    opts = ["rank-math-options-titles"] if any(x.get("target", {}).get("kind") == "option" for x in plan) else []
    json.dump({"approved_by": f"{os.environ.get('USER')} via seo push {time.strftime('%Y-%m-%d %H:%M')}", "what": f"on-page swap {os.path.basename(d)}",
               "posts": posts, "options": opts, "allow_new_posts": False}, open(f"{d}/scope.json", "w"))
    upload(s, [os.path.join(HERE, "apply.php"), os.path.join(HERE, "guard.php"), f"{d}/plan.json", f"{d}/scope.json"])
    ssh(s, "grep -q g_check_live ~/hhl-scripts/guard.php 2>/dev/null || cp ~/seo-onpage/guard.php ~/hhl-scripts/guard.php")
    env = f"SEO_KIT=1 SCOPE=~/seo-onpage/scope.json PLAN=~/seo-onpage/plan.json" + (" APPROVE_GLOBAL=1" if approve_globals else "") + (" DRY=1" if dry else "")
    out = wp(s, "eval-file ~/seo-onpage/apply.php", env=env); open(f"{d}/apply.txt", "w").write(out); print(out)
    if dry: return
    for line in out.splitlines():
        if line.startswith("backups: "): open(f"{d}/backup.txt", "w").write(line.split(": ", 1)[1].strip())
    purge(s)
    if s.get("hosting") == "ghl":
        input("\nGHL hosting: open the site in GHL → WordPress → Clear Cache, click it, then press Enter here... ")
    subprocess.run([sys.executable, os.path.join(HERE, "settle.py"), f"{d}/plan.json", s["base"], "300" if s.get("hosting") == "ghl" else "180"], check=False)
    paths = sorted({x["path"] for x in plan})
    locate(s, paths, f"{d}/live-after.json")
    subprocess.run(["node", os.path.join(HERE, "snapshot.cjs"), f"{d}/plan.json", s["base"], f"{d}/after.json", "after"], check=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, "verify.py"), f"{d}/plan.json", f"{d}/live-after.json", "--before", f"{d}/before.json", "--after", f"{d}/after.json", "-o", f"{d}/verify.html"])
    if not os.environ.get("SEO_NO_OPEN"): subprocess.run(["open", f"{d}/verify.html"], check=False)
    if r.returncode: print("\nSome rows FAILED verification. Read verify.html; if it looks wrong: seo rollback", key)

def cmd_pick(key, row, choice):
    d = run_dir(key); plan = json.load(open(f"{d}/plan.json")); live = {o["path"]: o for o in json.load(open(f"{d}/live.json"))}
    x = plan[int(row)]
    if x.get("status") != "pick": sys.exit(f"row {row} is {x.get('status')}, not a pick row")
    if choice == "new":
        x.update(status="blocked", why="a NEW heading = a new element: send to Beckett")
    else:
        o = x["options"][int(choice) - 1]
        t = next(t for t in live[x["path"]]["texts"] if t["el"] == o["el"] and t["text"] == o["text"])
        x.update(status="ready" if t["source"] == "page" else "global", post=t["post"], el=t["el"], widget=t["widget"], field=t["field"],
                 inline=bool(t.get("inline")), now=t["text"], old_tag=t["tag"], tag=x.get("tag") or t["tag"], source=t["source"],
                 why=f"picked by hand: replaces \"{t['text']}\"")
    json.dump(plan, open(f"{d}/plan.json", "w"), indent=1, ensure_ascii=False)
    subprocess.run([sys.executable, os.path.join(HERE, "plan.py"), "--report-only", f"{d}/plan.json", "-o", d], check=False)
    print(f"row {row}: {x['status']}  {x.get('why','')}")

def cmd_rollback(key, stamp=None, force=False):
    s = site(key); d = run_dir(key, stamp)
    if not os.path.exists(f"{d}/backup.txt"): sys.exit(f"{os.path.basename(d)} was never pushed: nothing to roll back")
    pushed = sorted(x for x in os.listdir(os.path.join(RUNS, key)) if os.path.exists(os.path.join(RUNS, key, x, "backup.txt")))
    if pushed and os.path.basename(d) != pushed[-1] and not force:
        sys.exit(f"{os.path.basename(d)} is not the newest push ({pushed[-1]} is). Rolling it back would also undo everything pushed since. "
                 "Roll back the newer ones first, or add --force if you're sure.")
    b = open(f"{d}/backup.txt").read().strip()
    upload(s, [os.path.join(HERE, "restore.php")])
    upload(s, [f"{d}/scope.json"])
    print(wp(s, "eval-file ~/seo-onpage/restore.php", env=f"SEO_KIT=1 SCOPE=~/seo-onpage/scope.json BACKUP={b}")); purge(s)
    os.rename(f"{d}/backup.txt", f"{d}/backup.rolled-back.txt")

def cmd_access(key):
    s = site(key); ok = lambda m: print(f"  ✓ {m}"); bad = lambda m: print(f"  ✗ {m}")
    try: v = wp(s, "core version", env="READONLY=1").strip().splitlines()[-1]; ok(f"SSH + WP-CLI ({s['hosting']}): WordPress {v}")
    except SystemExit as e: bad(f"SSH: {e}"); return
    for plug in ("elementor", "seo-by-rank-math"):
        st = wp(s, f"plugin is-active {plug} && echo yes || echo no", env="READONLY=1").strip().splitlines()[-1]
        (ok if st == "yes" else bad)(f"plugin {plug}: {'active' if st == 'yes' else 'NOT active'}")
    g = ssh(s, "test -f ~/hhl-scripts/guard.php && echo yes || echo no", check=False).strip()
    (ok if g == "yes" else bad)("write guard installed" if g == "yes" else "write guard missing (seo push installs it)")
    code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", s["base"]], capture_output=True, text=True).stdout
    (ok if code == "200" else bad)(f"site answers {code} at {s['base']}")

def cmd_log(text):
    os.makedirs(CONF, exist_ok=True)
    with open(os.path.join(CONF, "issues.jsonl"), "a") as f: f.write(json.dumps({"at": time.strftime("%Y-%m-%d %H:%M"), "issue": text}) + "\n")
    print("logged. It joins the rulebook the next time the skill starts (references/rulebook.json + your issues.jsonl).")

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help", "help"): print(__doc__); sys.exit()
    c = a[0]
    if c == "sites": [print(f"{k:16} {v['base']}  ({v['hosting']})") for k, v in sites().items()]
    elif c == "access": cmd_access(a[1])
    elif c == "audit": subprocess.run([sys.executable, os.path.join(HERE, "audit.py"), a[1]], check=True)
    elif c == "plan": cmd_plan(a[1], a[2])
    elif c == "push": cmd_push(a[1], "--globals" in a, "--dry" in a)
    elif c == "pick": cmd_pick(a[1], a[2], a[3])
    elif c == "rollback": cmd_rollback(a[1], next((x for x in a[2:] if not x.startswith("--")), None), "--force" in a)
    elif c == "log": cmd_log(" ".join(a[1:]))
    else: print(__doc__)
