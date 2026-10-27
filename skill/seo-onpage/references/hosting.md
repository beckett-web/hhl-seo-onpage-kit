# Hosting: where our client sites live and what changes between them

Two hosts, same tool. The difference is only how you get in and how the cache clears.

| | Cloudways | GHL WordPress hosting |
|---|---|---|
| Who | Most FSO sites (Elevation, WesCo, LCC, Dobbins...) | Sunshine State, Legacy, some older client sites |
| Tell-tale | the domain points at `159.203.65.36` | the domain is a CNAME to `*.wpdns.site` |
| Get in | SSH with your key: an app user per client app (Beckett adds it) | SSH with your key, one per site (Beckett imports it in the site's Advanced Settings) |
| WP-CLI | normal | always add `--skip-plugins=novamira` (the tool does it when `"hosting": "ghl"`) |
| Caches | Elementor CSS → Seraphinite page cache → Varnish (needs the Host header) → Cloudflare if it's proxied | GHL's own page cache: only the **Clear Cache** button in the site panel clears it |
| Purge | automatic in `seo push` (the `purge` list in sites.json) | `seo push` tells you to click Clear Cache, then keeps checking until phone + desktop copies are fresh |
| Domain's Cloudflare | DNS only (grey cloud) on our go-lives | the client's own Cloudflare zone is NOT in the request path: don't purge it expecting a change |

## Elevation specifically
- Lives on Cloudways today (app 6724837). **We may move it to GHL WordPress hosting later.** If that happens, only its
  row in `sites.json` changes (`hosting`, `host`, `user`, `wp_path`, `purge`); the doc, plan and push work the same.
  After a move, run `seo audit elevation` again before your next push: element ids survive a migration, but check.
- It's a two-market site: `/` is the Colorado home (it holds the old site's Colorado rankings), Florida lives under
  `/florida/`. Each market has its own nav, phone and footer (set per page, don't edit those).
- Its pages were built by our build scripts. A kit push stamps each page it touches so our next build skips it.

## How to tell which host a new client is on
`dig +short www.<domain> CNAME` → `*.wpdns.site` = GHL. `dig +short www.<domain>` → `159.203.65.36` = Cloudways.
Anything else: ask Beckett before doing anything.
