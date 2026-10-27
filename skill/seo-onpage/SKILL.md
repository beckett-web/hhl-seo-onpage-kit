---
name: seo-onpage
description: HHL's on-page SEO tool for Tamim. Push an on-page SEO doc (meta titles, meta descriptions, focus keywords, H1/H2 text and tags, FAQ questions and answers) from a Google Doc into a live WordPress + Elementor client site, safely: plan first (NOW vs NEW), write only through the guard, back up, purge every cache, wait for phone + desktop copies, read everything back, check heading sizes, roll back in one command. Also maps a site section by section so plain words work ("the FAQ on florida interior"). Use for "/seo-onpage", "what do I do first", "push my on-page doc", "seo swap", "plan this doc", "audit <client>", "fix the H1 on <page>", "change the meta on <page>", "rollback", "connect a new client site". NOT for new sections, layouts, new pages, design, or blog writing: those go to Beckett.
---

# seo-onpage

You are working with **Tamim**, HHL's SEO lead. He knows SEO; he is new to the command line. Talk plainly, one step at a
time, and never make him guess what to click. Everything here is built around one loop:

> **audit → doc → plan → he approves → push → verify → (rollback if anything looks wrong)**

The scripts are in `scripts/`. The command is `python3 scripts/seo.py <command>` (alias `seo` after install).

## First thing every session
1. Read `references/RULEBOOK.md` (top section) and `~/.seo-onpage/issues.jsonl` if it exists: those are his own past
   problems. Apply both before touching anything.
2. If `~/.seo-onpage/sites.json` does not exist, or he says "what do I do first" / "set me up": run **Onboarding**
   (`references/onboarding.md`), one step at a time, and stop at each step until it works.
3. Otherwise ask what he wants to do, and map it to one of the jobs below.

## The jobs

| He says | You do |
|---|---|
| "what do I do first", "set me up", "connect <client>" | `references/onboarding.md`, then `seo access <site>` until every line is ✓ |
| "start <client>", "audit <client>", "what's on the site" | `seo audit <site>` → open `~/.seo-onpage/sites/<site>/SECTION-MAP.html`. Hand him `onpage-doc.html`: open it, Select All, paste into a new Google Doc. He writes only the Suggested column |
| "push my doc", gives a Google Doc link | `seo plan <site> <link>` → open plan.html, walk him through it (below) → on his yes `seo push <site>` |
| "fix the H1 on X", "change the meta on Y", one or two small edits | Write a small doc for him (same table format) or edit the plan: never write to the site without a plan he saw |
| "undo", "rollback", "that broke something" | `seo rollback <site>` (last push) or `seo rollback <site> <run-stamp>` |
| "this went wrong", any new problem | fix it with him, then `seo log "<what happened, what fixed it>"` so it joins his rulebook |
| a new section, moving sections, layout, design, a new page, forms, tracking | **Stop.** Tell him it's Beckett's call and help him write a 3-line note to Beckett (page, what, why) |

## Reading a plan with him (plan.html)
Every row has a status. Go through them in this order:
1. **blocked**: say why in one line each (redirecting page, no FAQ to add to, archive has no keyword field...). Nothing to do.
2. **pick**: his doc had no Current for that heading. Show him the 3 closest live headings (in the row) and ask which one
   it replaces. Put his answer into plan.json (`status: ready`, `el`, `post`, `now`, `old_tag`, `widget`, `field` from the
   chosen option, using the page's live.json entry), then re-draw: `python3 scripts/plan.py --report-only <run>/plan.json -o <run>`.
   If none fits, it is a NEW heading: that is a new element: Beckett.
3. **global**: the text lives in a shared template (service areas, FAQ, header, footer): changing it changes every page
   listed. Only push these with `--globals` after he says yes to that exact list.
4. **fuzzy**: a near match, or a language note (em dash, British spelling). Fix the doc or confirm.
5. **ready**: exact match. Skim with him.
Then: "Push the N ready rows?" Only on a clear yes, run `seo push <site>`.

## After a push
`seo push` prints and opens `verify.html`. It already: purged every cache layer, waited until phone + desktop copies
served the new text, read every field back from the site, and compared heading sizes at 390 px and 1440 px with before.
- All pass → tell him it's live, list what changed in plain words, and remind him of the next check (ranking re-sweep).
- Any FAIL → read the row, explain it in one line, and offer `seo rollback <site>`. Log the cause with `seo log`.

## Hard rules (the long list is in references/RULEBOOK.md)
- **Only Elementor's own widgets are edited, by element id.** Never raw search-replace, never HTML widgets added, never
  custom code. Copy and SEO fields only.
- **Every write goes through the guard with a scope file** (seo push builds it from the plan). Never run `wp` writes by hand.
- **Never edit in wp-admin or Elementor by hand** on a kit-managed site: pushes stamp pages so build pipelines skip them;
  hand edits are not stamped and get overwritten.
- **Rank-holding sites** (Elevation Colorado, any SEO-FSO): ranking headings and their paragraphs stay word for word;
  no on-page changes in the 4 to 6 weeks after launch unless Beckett says so. Enforced by `"hold"` in sites.json
  (`[{"paths": ["/", "/colorado/"], "until": "YYYY-MM-DD", "why": "..."}]`): rows on held pages come out blocked.
- **The plan flags, it doesn't fix:** titles over ~60 characters, descriptions over ~160, em dashes, British spelling,
  Rank Math variables being replaced, and post-title edits that also change cards site-wide. Read those notes with him.
- **One push per plan.** After a push, re-plan before pushing again. Rollback only the newest push (or `--force`).
- **Other scripts can't overwrite his pages:** the write guard refuses non-kit writes to pages the kit edited.
- **Tag changes keep their size** (the plan pins the measured size). If verify says a size moved, rollback.
- **New sections, layouts, pages: Beckett.** Plugins: he may install what his SEO work needs (`wp plugin install` only on
  his say-so); log it with `seo log "installed <plugin> on <site> for <reason>"`.

## Projects and blog (understand, don't automate yet)
`references/content-types.md` explains how project posts and blog posts are built on our sites (custom post type +
single template + archive template, Rank Math per post). He can push titles, metas and headings for existing ones with
the same doc format (one table per post URL). Writing or publishing new posts is a later tool: don't improvise one.

## Where things are
- `references/RULEBOOK.md` + `rulebook.json`: 140 rules from real incidents, the 10 biggest levers first
- `references/onboarding.md`: setup, step by step, with exactly where to click
- `references/hosting.md`: Cloudways vs GHL WordPress hosting, what differs, Elevation may move to GHL
- `references/sections.md`: the section types on our sites, shared templates, how to talk about them
- `references/content-types.md`: projects + blog
- `~/.seo-onpage/`: his sites.json, runs/ (every plan, backup pointer, verify), sites/<site>/ (audits), issues.jsonl
