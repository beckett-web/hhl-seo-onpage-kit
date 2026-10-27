# Onboarding: from zero to your first push

Walk Tamim through these one at a time. Do each step, check it worked, then the next. Never paste a key or password
into chat: he keeps them on his own machine. Where a step happens in a browser, open the exact page for him with
`open <url>` and tell him what to click on that screen. If `onboarding/shots/<step>.png` exists, show it.

## 1. The tools on his computer (once)
- Claude Code: already running if he's reading this.
- `./install.sh` from the repo folder. It checks python3, node, git; installs the Python + Playwright pieces; links this
  skill into `~/.claude/skills/seo-onpage`; adds the `seo` command; creates `~/.seo-onpage/` with an empty `sites.json`.
- Check: `seo --help` prints the command list.

## 2. His own SSH key (once)
This is the only key the core work needs: it lets the tool reach a client's WordPress over SSH, with no passwords.
```bash
ssh-keygen -t rsa -b 4096 -C "tamim@hardhatlaunch.com" -f ~/.ssh/hhl_seo
```
(RSA, not ed25519: GHL hosting refuses ed25519.) Press Enter twice for no passphrase, or set one and add it to the
keychain: `ssh-add --apple-use-keychain ~/.ssh/hhl_seo`.
Then: `pbcopy < ~/.ssh/hhl_seo.pub` and send that ONE line (the `.pub`, never the other file) to Beckett on Slack.
That public half is safe to share.

## 3. Beckett adds that key to each client site (Beckett's step, per client)
Tell Tamim to wait for Beckett's "done" for each client. What Beckett does:
- **Cloudways** (most FSO sites): platform.cloudways.com → Applications → the client's app → **Access Details** →
  Application Credentials → add an SSH key for an app user (paste Tamim's `.pub`). An app user reaches that ONE app only.
  Beckett sends back: the server IP, the app username, and the app URL.
  (Fallback if app-level keys aren't available on the plan: Server → Master Credentials → SSH Public Keys. That key
  reaches every app on the server, so Beckett removes it when Tamim no longer needs it.)
- **GHL WordPress hosting**: GHL → Sites → WordPress → the site → **Advanced Settings → Access SSH → Manage SSH Keys** →
  import the `.pub`. The same panel shows the SSH username and host: Beckett sends those.

## 4. Add the site to his sites.json
Fill one row per client in `~/.seo-onpage/sites.json` (copy `sites.example.json`):
```json
{"elevation": {"name": "Elevation Painting", "hosting": "cloudways",
  "base": "https://www.elevationpaintingllc.com",
  "host": "159.203.65.36", "user": "<app username Beckett sent>", "key": "~/.ssh/hhl_seo",
  "wp_path": "~/public_html",
  "purge": ["wp elementor flush-css >/dev/null 2>&1",
            "rm -rf wp-content/cache/seraphinite-accelerator/* 2>/dev/null"]}}
```
Rank-holding pages get a hold (Elevation: `"hold": [{"paths": ["/", "/colorado/"], "until": "2026-12-03", "why": "Colorado
rankings hold, 6 weeks after launch"}]`): Beckett sets it, and the plan blocks those pages until the date.
GHL rows: `"hosting": "ghl"`, `user` + `host` from the panel, `"port": 22`, `wp_path` as the panel shows, and
`"purge": []` (GHL's page cache is cleared with the **Clear Cache** button in the site panel: `seo push` tells him when).
Then: `seo access <site>`. Every line must be ✓. If SSH fails: wrong user/host, or Beckett hasn't added the key yet.

## 5. Map the site (once per client, and after big changes)
`seo audit <site>` → opens `SECTION-MAP.html` (every page, section by section, with screenshots) and writes
`onpage-doc.html`: the on-page doc already filled with the live titles, metas, H1s, H2s and FAQs.

## 6. His doc
Open `onpage-doc.html` in the browser → Select All → Copy → paste into a new Google Doc. Write only the **Suggested**
column. Rules for the doc:
- Leave Suggested empty (or write "Keep as is") to keep a row.
- Change a tag with `<H2> New heading text </H2>` (or `<P>` to make an H1 a plain line).
- New FAQ: a FAQ row with Current empty and `Question? (Answer: the answer.)`.
- Share → "Anyone with the link: Viewer" (the tool reads it without a login).

## 7. First push
`seo plan <site> <doc link>` → read plan.html with Claude → `seo pick` any pick rows → `seo push <site>` → verify.html.
Start with ONE page the first time.

## Optional keys (later, only when a job needs them)
Search Console, GA4 and any other API come later. When he gets a key: `scripts/savekey NAME value` stores it in
`~/.seo-onpage/keys.env` (his machine only, loaded by the tools). Never in sites.json, never in the repo, never in chat.
