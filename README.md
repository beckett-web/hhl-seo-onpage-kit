# HHL seo-onpage

Push an on-page SEO doc from a Google Doc into a live WordPress + Elementor client site, safely, from Claude Code.

**What it does:** maps a site section by section → gives you a ready on-page doc with every live title, meta, H1, H2 and
FAQ filled in → you write the Suggested column in Google Docs → `seo plan` shows NOW vs NEW for every row → you approve →
`seo push` writes only what you approved, backs everything up, clears every cache, waits until phone and desktop copies
show the change, reads every field back and checks no heading changed size. `seo rollback` puts it all back.

**What it doesn't do:** new sections, layouts, new pages, design, forms, tracking. Those go to Beckett. No blog writing yet.

## Start
```bash
git clone https://github.com/beckett-web/hhl-seo-onpage-kit.git ~/hhl-seo-onpage && cd ~/hhl-seo-onpage && ./install.sh
```
Open a new terminal, run `claude`, type **`/seo-onpage`** and say **"what do I do first?"**. The skill walks you through
the rest (your SSH key, connecting each client site, your first audit, your first push).

## Commands
| | |
|---|---|
| `seo sites` | sites you can reach |
| `seo access <site>` | test the connection (every line should be ✓) |
| `seo audit <site>` | section map + a pre-filled on-page doc |
| `seo plan <site> <google-doc-link>` | NOW vs NEW for every row. Writes nothing |
| `seo pick <site> <row> <1-3\|new>` | answer a "which heading does this replace" row |
| `seo push <site>` | apply + purge + verify (add `--globals` only for shared-template rows you approved) |
| `seo rollback <site>` | undo the last push exactly |
| `seo log "<what happened>"` | add a problem to your issue log (the skill reads it every session) |

## Safety, in one line each
- Every write is limited to the pages in the approved plan (write guard + scope file).
- Every page is backed up before its first change; rollback restores it exactly.
- Edits go to Elementor's own widgets by element id. Nothing else on the page is touched.
- Shared templates (service areas, FAQ, header, footer) are never changed without an explicit yes.
- Pages you push are stamped so our build tools never overwrite your SEO work.
- Your keys stay on your machine (`~/.seo-onpage/`), never in this repo.

## Your files
`~/.seo-onpage/sites.json` (your sites), `runs/` (every plan, push and verify, by date), `sites/<site>/` (audits),
`issues.jsonl` (your issue log). Rules from every past incident: `skill/seo-onpage/references/RULEBOOK.md`.

Questions, new sections, anything outside on-page: Beckett.
