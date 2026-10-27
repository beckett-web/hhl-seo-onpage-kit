# On-page SEO rulebook · editing live client WordPress + Elementor sites

For Tamim, pushing on-page SEO edits through Claude Code: meta titles and descriptions, heading text and tags, paragraphs, FAQ items, schema. 140 rules (20 blockers, 43 high, 77 normal), every one from a real incident on an HHL site. Machine-readable copy: `rulebook.json` (same ids). Built 22 Oct 2026.

**Your lane:** copy and SEO fields on pages that already exist. **Not your lane:** new sections, layout, new pages, forms, plugins, theme PHP, tracking, DNS beyond a verification TXT. Those go to Beckett.

## The 10 biggest levers

1. **R011** Run every write with SCOPE=<WRITE-SCOPE.json> listing the exact post ids and option names, approved before the run, and every read with READONLY=1. *Nothing gets written that was not named and approved first; it also blocks raw SQL and blind search-replace.*
2. **R001** Edit only copy and SEO fields on existing pages (meta title, meta description, heading text, heading tag with its size rule, paragraphs, FAQ question and answer text, schema); never add, remove, move or restyle a section, change a layout or build a page: send those to Beckett. *Keeps every structural decision with Beckett; most past damage came from fixing more than was asked.*
3. **R111** Treat shared templates as site-wide edits: service areas 2478 (Sunset markets 6057, 6062, 6067, 6070), FAQ 9182 / 2873, header 14, footer 47, lead forms 9936 / 2535 / 2087; editing one changes every page that embeds it. *One edit in the wrong place changes every page; one edit in the right place saves sweeping eleven.*
4. **R055** Never change a heading's tag (H1/H2/H3) without keeping its size: template size rules target the tag (`selector h1`, `selector h2`), so a tag swap changes the rendered size. *The most likely SEO edit to break the layout on phones, and it already happened at Elevation's launch.*
5. **R035** After every write purge every layer in serving order: Elementor CSS + object cache, then Seraphinite's page cache, then Cloudways Varnish, then Cloudflare if it caches HTML. *Without it you report a fix that visitors cannot see (46 minutes on Ridgeline, 40 hours on Dobbins).*
6. **R043** Verify every change on the PLAIN canonical URL a visitor hits, never on a ?cb= or any query-string URL. *The single check that separates "the database changed" from "the visitor sees it".*
7. **R088** Write by element id and field; never string-replace raw _elementor_data. *Raw string swaps fail silently or corrupt half a sentence and report success.*
8. **R013** On Elevation (and any pipeline-built site) edit only through `seo push`: it stamps the page so the build push skips it. Never hand-edit in Elementor or wp-admin. *A hand edit is erased by the next build push; a kit edit is protected.*
9. **R074** Never write schema into Elementor Custom Code (_elementor_code) with update_post_meta from the CLI; write it with a direct guarded $wpdb update, read it back, and assert `<script` is present and the JSON parses. *One CLI write printed raw JSON on every page of a live client site.*
10. **R092** Keep every ranking heading and the paragraphs under it word for word on a rank-holding site; only em dash to comma and Tamim-approved H1 edits are allowed. *Protects the rankings the client already has; with the 4 to 6 week hold, every movement stays explainable.*

## Things you can skip (the push and verify tools do them)

You never run these by hand. If a tool ever skips one, that is a tool bug: report it.

- Purging Elementor CSS, Seraphinite, Varnish (with Host header) and checking Cloudflare after every push, in that order (R035, R036, R039)
- Warming the cache page by page after a purge (R040)
- Taking the database backup and the per-page revert file before the first write (R012)
- Writing the WRITE-SCOPE.json from your approved change list and running with SCOPE= (you approve it, the tool builds it) (R011)
- wp_slash + JSON validation on _elementor_data, element-id lookup, and keeping heading spans and tags balanced (R103, R058)
- Plain-URL verification with x-cache/age headers, DB read-back, H1 count, font-size compare at 390 and 1440 (R043, R044, R057, R055)
- Flagging em dashes and British spellings in your new text before anything is written (R051)
- Adding --skip-plugins=novamira on GHL sites and going through wpsite (R028, R022)

## Rules by area

Blockers first in each group. Format: **id** `severity` rule. *Why.*

### Scope: what you touch and what you escalate (10)

- **R001** `blocker` Edit only copy and SEO fields on existing pages (meta title, meta description, heading text, heading tag with its size rule, paragraphs, FAQ question and answer text, schema); never add, remove, move or restyle a section, change a layout or build a page: send those to Beckett. *Every structural change on a client site has been Beckett's call; the FSO rule is that only header, links, copy, colours and images change, and Yard Dogs' re-shaped buttons (Sep 2026) were caught by him.*
- **R002** `blocker` Never touch WordPress settings outside SEO copy: no plugin installs or removals, caching config, theme or plugin PHP, analytics or tracking IDs, blog_public, permalink structure, user accounts or the Elementor Kit. *Beckett, WesCo (Sep 2026): "The skill should never touch WordPress setting stuff"; those belong to Beckett or the dev.*
- **R003** `blocker` Do not edit or move the "Painting in Colorado + Florida" block on Elevation's home page. *It is the old home page's content, word for word, and carries 85 of the 89 rankings (sweep 12 Oct 2026).*
- **R004** `high` Never swap one template section for another, or replace a global shortcode block with a per-page copy (or the reverse), on your own call. *Elevation's market homes got Sunshine's town grid in place of the template's toggle and Beckett asked "When did I authorize that" (13 Oct 2026); globals stay globals.*
- **R005** `high` Treat any wp_options write (Rank Math identity, esci_* contact options) as a disclosed exception: name it in the scope file and on its own line in the report. *Some option writes are required (esci phone override, og:site_name) but the settings guardrail says they get their own line every time.*
- **R006** `high` If schema or tracking is hard-coded in theme PHP, a child theme or GTM, do not edit it: report where it lives and escalate. *ProWash's old agency schema lived in content.php/content-page.php and GTM and blocked the new Rank Math schema (May 2026); the PHP edit was not Tamim's to make.*
- **R007** `high` On a site that launched under SEO preserve, make no on-page changes for 4 to 6 weeks, then change one variable at a time. *Tamim's own rule from the Yard Dogs doc, applied to Elevation (launched 22 Oct 2026, re-sweep 29 Oct): if rankings move you must know why.*
- **R008** `normal` Note out-of-scope problems you find and report them; never fix them in passing. *FSO stage 8 rule: execute the approved work order and nothing else, so every change on a client site has an owner.*
- **R009** `normal` Never add a block that already exists on the page (a second FAQ, trust strip or location block) to get more keywords in. *Mehedi declined to duplicate a services block on ProWash for duplicate content (May 2026) and Beckett agreed.*
- **R010** `normal` Never create legal pages, new pages or new posts; a write that creates a post needs allow_new_posts, which is Beckett's. *Eight sites have no legal pages and Beckett parked them ("market-wide PP and TOS later", 22 Sep 2026); page creation is his.*

### Process (11)

- **R011** `blocker` Run every write with SCOPE=<WRITE-SCOPE.json> listing the exact post ids and option names, approved before the run, and every read with READONLY=1. *The write guard exists because unscoped writes damaged live pages; eval-file with neither declaration is blocked by the hook.*
- **R012** `blocker` Take `wp db export` before every write session and keep a per-page revert JSON of _elementor_data plus the rank_math pair. *Every recovery so far (Dobbins clone scrub hitting Yard Dogs, restored in 2 minutes on 5 Oct 2026) depended on a backup taken first.*
- **R013** `blocker` On Elevation, never edit a page in Elementor or wp-admin by hand: change the build source (make_fill.py output) or the seo layer and push, because push.php overwrites the live page on the next run. *Pages are generated by make_fill.py and pushed by push.php; the handover to Tamim (22 Oct 2026) says a manual Elementor edit gets overwritten. There is no live-edited flag yet: push.php only skips the 'home' row.*
- **R014** `high` After anyone edits a page in wp-admin, change it only with targeted ops on the LIVE data; never re-push a whole page compiled from an older pull. *Yard Dogs (30 Sep 2026): a late copy change nearly wiped the form webhooks Beckett had just mapped in wp-admin.*
- **R015** `high` Dry-run every multi-page or site-wide change and read the scope report before applying it. *A live search-replace with no dry run damaged the About page heading; the hook now blocks it.*
- **R016** `normal` Keep copy as data (a JSON or sheet of page, element id, field, new value) and generate the write from it; never hand-type copy into a PHP script. *The Sunshine and Elevation fills only stayed consistent because copy came from one structured source (services-copy.py, make_fill.py).*
- **R017** `normal` Say what you did not do in the same breath as "done" ("done except X"). *Ridgeline: "the project posts are done" was said while all six still read Bonita Springs, Florida.*
- **R018** `normal` Read the whole list before claiming something does not exist (post types, menus, templates, redirects). *A truncated `wp post-type list` produced a confident wrong claim that a CPT was missing.*
- **R019** `normal` After two failed blind fixes, stop and instrument (or escalate) instead of trying a third. *Sunshine (Aug 2026): two Chromium-based mobile fixes made the live site worse, one locked iOS scrolling.*
- **R020** `normal` Log every new miss as one line in the misses ledger or fix ledger, written as a default for next time. *Beckett (30 Sep 2026): "all these mistakes we caught, this should never happen again."*
- **R021** `normal` Commit only the client paths you changed (`git add <paths>`), never `git commit -am`. *Yard Dogs (30 Sep 2026): commit -am swept other projects' files in the shared workspace.*

### Access (6)

- **R022** `blocker` Reach a client site only through its row in ~/HHL/sites.json and `wpsite <key>`; if the site is not there, fingerprint the host and ask Beckett for the one missing piece. *The registry is the single source of truth (19 Sep 2026) and wpsite runs the write guard on the exact command it builds.*
- **R023** `blocker` Never edit the Cloudways copies of Sunset (app 6324586) or Legacy (app 6324601): the live sites are on GHL hosting. *Both Cloudways apps are old copies; edits there change nothing a visitor sees and can be mistaken for the live site.*
- **R024** `high` Confirm the target app by its home URL and sys_user before writing; never select an app by "newest" or by name match. *Dobbins (5 Oct 2026): a script took the newest app on the shared server and started scrubbing Yard Dogs' staging site.*
- **R025** `high` Write through `wp eval-file` (WP-CLI), never the REST API. *On GHL hosting app-password REST writes are capability-stripped even for an admin (Sunshine, 10 Aug 2026); WP-CLI runs as system.*
- **R026** `normal` Put config files for server-side scripts in ~/tmp on the server: wpsite does not pass local environment variables through. *Sunset market stamp (Oct 2026): scripts read ~/tmp/*.json on the server because env vars never arrived.*
- **R027** `normal` Keep MCP connectors and Novamira off production writes; production writes are SSH + WP-CLI only. *A community MCP returned HTTP 200 and "success" while the page went blank (research, Oct 2026).*

### GHL WordPress hosting (5)

- **R028** `blocker` On GHL-hosted WordPress add --skip-plugins=novamira to every wp command. *Novamira fatals under the CLI's PHP 7.4 ("unexpected ':'") on Sunshine, Legacy and Sunset; without the flag every command dies with a critical error.*
- **R029** `high` After a write on GHL hosting, purge GHL's edge: the site's mu-plugin `CDN_Clear_Cache_Api::cache_api_call([],"purge_everything")` where configured, otherwise ask Beckett to press GHL panel > Advanced Settings > Cache management > Clear Cache. *GHL's Cloudflare caches HTML with s-maxage 30 days; Bespoke's drafted blog stayed public until the panel purge (16 Oct 2026). The mu-plugin is inert without CDN_SITE_ID/CDN_SITE_TOKEN in wp-config (Legacy has them).*
- **R030** `normal` Do not set headers, caching or page rules in the client's own Cloudflare zone for a GHL-hosted site: that zone is not in the request path. *Sunshine (24 Aug 2026): zone settings were accepted and read back but never reached a visitor; GHL fronts with its own Cloudflare.*
- **R031** `normal` To hide a blog on GHL WordPress, unset Settings > Reading > Posts page (page_for_posts 0) as well as drafting the page, then clear the GHL edge. *Bespoke (16 Oct 2026): a drafted Posts page stays public because WordPress ignores draft status for it.*
- **R032** `normal` Never run two crawlers at the same time against a GHL-hosted site. *Sunset (14 Oct 2026): parallel crawls got 429s and the results had to be thrown away.*

### Cloudways hosting (2)

- **R033** `high` On Cloudways, verify that Seraphinite's host map matches the live domain; after a domain change it must be rebuilt (seraph-dropin.php) or nothing is cached or optimised. *Yard Dogs (30 Sep 2026): the clone kept the donor host in advanced-cache.php, mobile PageSpeed sat at 60 until the drop-in was rebuilt.*
- **R034** `normal` A 500 on save is usually the server memory limit: stop and escalate, do not retry the write in a loop. *Mehedi (10 Jul 2026): "This problem comes from low memory."*

### Cache (8)

- **R035** `blocker` After every write purge every layer in serving order: Elementor CSS + object cache, then Seraphinite's page cache, then Cloudways Varnish, then Cloudflare if it caches HTML. *Ridgeline showed corrected stats to every cache-busted check and the old stats to Beckett for 46 minutes; WesCo served the previous client's homepage for hours from 903 Seraphinite files.*
- **R036** `blocker` Send Varnish PURGE with the site's Host header (`-H "Host: <domain>"`), per URL, or with X-Purge-Method: regex for the whole site. *Dobbins (15 Oct 2026): PURGE to 127.0.0.1:8080 without Host returned 200 and purged nothing; the client saw a 40-hour-old page.* (Since 26 Oct 2026 Varnish is OFF on our Cloudways server: Seraphinite is the only page cache. On GHL hosting the layer above Seraphinite is GHL's Rocket.net CDN: purge it with the site panel's Clear Cache.)
- **R037** `high` Purge Seraphinite per URL with `seraph_accel\API::OperateCache(2, "<full url>")`; a post id does nothing. *Elevation About team edit (16 Oct 2026) stayed stale until the full-URL call plus a Varnish PURGE with Host.*
- **R038** `high` Remember `wp cache flush` clears only the WordPress object cache, not the page cache visitors get. *Ridgeline (Aug 2026): object cache flushed, Varnish kept serving the pre-edit HTML.*
- **R039** `high` After writing _elementor_data, clear that post's generated CSS and element cache (`wp elementor flush-css`, or delete its _elementor_css and _elementor_element_cache meta). *Elementor can serve a page's element tree and CSS from its own cache, so the DB changes while the page does not; Elevation's spelling pass deletes _elementor_css after each write.*
- **R040** `normal` Warm the cache one page at a time (about 2 seconds apart) after a full purge, never in parallel. *A parallel warm of 11 pages on a cold Cloudways site drove load to 9.5 and pages timed out right before a hand-off.*
- **R041** `normal` If cf-cache-status is HIT on HTML, Cloudflare needs its own purge; our token cannot purge, so tell Beckett. *CLOUDFLARE_API_TOKEN has no Cache Purge permission (8 Oct 2026); DYNAMIC means Cloudflare is not the problem.*
- **R042** `normal` After a slug change, flush Rank Math's sitemap cache (delete the %rank_math_sitemap% option rows and call Cache::invalidate_storage()). *Sunshine (27 Aug 2026): the Rank Math sitemap kept listing stale slugs long after the change.*

### Verify (12)

- **R043** `blocker` Verify every change on the PLAIN canonical URL a visitor hits, never on a ?cb= or any query-string URL. *A query string bypasses Seraphinite and Varnish, so it proves the DB and nothing else; a stale homepage shipped twice this way (Ridgeline 46 min, WesCo hours).*
- **R044** `high` Read every write back from the database AND from the rendered page; a script's success log or a 200 is never proof. *A tool that reports "35 elements updated / NOT FOUND: none" only proves it found the 35 it was asked for (Ridgeline); a vendor 200 has lied repeatedly.*
- **R045** `high` Report DB presence and rendered presence separately, and count only published posts, never revisions. *Legacy (11 Aug 2026): an asbestos licence was called "live and public" off a DB hit with zero hits on the page; "1,023 rows" was about 768 revisions, the real number was 92.*
- **R046** `normal` Grep the tag-stripped rendered text for visible copy, and the raw HTML for text hiding in attributes, CSS content:, and JSON-LD. *Sunshine copy hid in attributes, body classes and JSON-LD where a human never looked; a CSS ::after printed "Serving Southwest Florida" that no text grep saw (Ridgeline).*
- **R047** `normal` When capturing page text, open every accordion and tab and harvest each panel as it opens. *WesCo landscaping page: all 5 FAQ questions and 4 of 5 answers were missing from the capture; about 100 text slots sitewide were invisible to the gate.*
- **R048** `normal` Never judge a visibility or animation bug from a headless or background browser. *The "blank hero" bug (Aug 2026) was a measurement artifact: IntersectionObserver never fires in a hidden pane; real devices were fine.*
- **R049** `normal` Use headless Playwright for site checks, never Beckett's own browser. *Standing rule: site checks must not take over his Chrome or screen.*
- **R050** `normal` Read the sitemap's slugs (post-sitemap.xml, page-sitemap.xml) after any rewrite, not just the pages. *Sunshine (Aug 2026): 8 blog posts were windows content on roofing URLs for months because reviewers read titles and the sitemap holds URLs.*
- **R051** `normal` Run the language audit after every copy push: em dashes, British spellings, repeated words, placeholders, periods. *WesCo shipped "neighbourhoods" and "kerb" on a Florida site and four review agents missed both.*
- **R052** `normal` Check blog_public = 1 and no noindex meta on the live domain whenever you audit a launched site; never change it yourself. *WesCo (10 Sep 2026) went live with blog_public still 0, a finished site telling Google to index nothing.*
- **R053** `normal` After a rank-holding launch, re-sweep with the same seo.config.json one week later and, for any lost ranking, compare that page to its preserve list first. *The SEO FSO track (Yard Dogs, Elevation re-sweep 29 Oct 2026) depends on a before/after on identical searches.*
- **R054** `normal` Count headings on the rendered page at both 1440 and 390, because some themes print a different block per breakpoint. *Yard Dogs' old theme rendered sections twice (desktop and mobile copies), doubling raw heading counts.*

### Headings (11)

- **R055** `blocker` Never change a heading's tag (H1/H2/H3) without keeping its size: template size rules target the tag (`selector h1`, `selector h2`), so a tag swap changes the rendered size. *Elevation launch (22 Oct 2026): the hero heading demoted for SEO rendered at 62px instead of 35px on phones; 577 tag-bound rules exist sitewide.*
- **R056** `high` When a heading tag changes, the widget's custom CSS selector must be re-aimed to the new tag in the same change; if the tool cannot do that safely, escalate instead of swapping the tag. *Tamim's May 2026 hero H1 changes broke sizes on market, about and service pages until Mehedi swapped `h2` to `h1` in the CSS; batch fix on Legacy, Cold Iron and Mako 23 May.*
- **R057** `high` Keep exactly one H1 per page. *Duplicated pages without _elementor_page_settings print the WP page title as a second H1 (Ridgeline); HHL's own WP home once had 5 H1s used as section labels.*
- **R058** `high` Keep the accent <span> (and any <br>) inside a heading when you rewrite its text; write `Simple as <span>1-2-3</span>`, not the plain string. *About 15 headings lost their accent word on WesCo when plain text was written over the span (Aug 2026).*
- **R059** `normal` Make the H1 the exact target keyword with no selling words in front; selling words and the phone go in the meta title and description. *Tamim's rule (30 Jul 2026); "FL" and "Florida" are treated the same and the abbreviation keeps titles short.*
- **R060** `normal` On ProWash the service hero H1 is the page title and the excerpt is the paragraph under it; changing the H1 means changing post_title, and they cannot differ there. *Mehedi (10 May 2026): the ProWash template reads the title into the hero; a separate H1 needs a template rebuild.*
- **R061** `normal` Write headings in sentence case and check the rendered text: template CSS (`text-transform: capitalize`) or Rank Math capitalize_titles can turn "in" into "In". *Yard Dogs ("And Surrounding Areas", 30 Sep 2026) and Dobbins ("In Boca", 5 Oct 2026).*
- **R062** `normal` No heading takes a period; every paragraph and sentence-like line does. *House rule from the language pass (8 Sep 2026); a client caught a descriptive line with no period under a heading.*
- **R063** `normal` Never open two pages with the same H2. *Beckett ruling on LCC (15 Sep 2026): keep it on the page it belongs to, use another of the client's lines on the second.*
- **R064** `normal` Keep heading levels in order (no skipped rung) and give each sub-service one H3 with 60 to 120 words under it. *Site audit HEAD family flags skipped levels; Tamim's sub-service rule for Elevation (12 Oct 2026).*
- **R065** `normal` Keep a rewritten heading close to the old one's length; line breaks come from the widget's max width, not <br>. *Mehedi: copy length is a layout input ("If you write a big word like average there then it will not work"); a long heading can stack one word per line (LCC ruling).*

### Meta titles, descriptions, Rank Math (8)

- **R066** `blocker` Rank Math settings live in hyphen-named options (rank-math-options-titles, rank-math-options-general); merge single keys, never write the whole option. *Yard Dogs (30 Sep 2026): the first scrub used the wrong names and only reset knowledgegraph_name; a whole-option write wipes the array.*
- **R067** `high` Set rank_math_title and rank_math_description explicitly on every page you touch; never leave the description empty. *Empty descriptions fall back to %excerpt% or post_content, which held donor copy (Yard Dogs "Veteran-owned ... Bradenton", Sunshine's Fort Myers page sharing as "Collier County").*
- **R068** `high` Copy preserved titles and meta descriptions verbatim on a rank-holding site; the only approved edits are the ones on the preserve list. *Yard Dogs and Elevation: Google titles and descriptions carried word for word (one approved change: a dash to a pipe on the Yard Dogs home).*
- **R069** `normal` Keep Rank Math capitalize_titles off. *With it on, client exact titles change ("in" becomes "In"), which matters on rank-holding sites (Yard Dogs).*
- **R070** `normal` Keep titles under about 62 characters and unique per page; never "Home" or a placeholder. *Site audit HEAD family flags titles over 62; Elevation's sitecheck asserts unique titles.*
- **R071** `normal` Remember post_excerpt is printed by card grids on the home and hub pages, not on the page you are editing. *Ridgeline/Sunshine: wrong excerpts showed in the home services grid while the page itself looked right.*
- **R072** `normal` Set og:image per page through rank_math_facebook_image_id (the id beats the url), with homepage_facebook_image and open_graph_image as the fallbacks. *Setting only the URL changes nothing; Rank Math falls back to the featured image, which put a WesCo photo in Yard Dogs' iMessage preview (30 Sep 2026).*
- **R073** `normal` Leave deliberate noindex on demo or filler posts (rank_math_robots noindex) alone. *Clone-carried blog posts ship noindex on purpose; Rank Math drops them from the sitemap.*

### Schema (9)

- **R074** `blocker` Never write schema into Elementor Custom Code (_elementor_code) with update_post_meta from the CLI; write it with a direct guarded $wpdb update, read it back, and assert `<script` is present and the JSON parses. *Mako (19 Oct 2026): the CLI write ran as user 0 without unfiltered_html, the script wrapper was stripped and raw schema JSON printed on every page; kses_remove_filters() did not stop it.*
- **R075** `high` After any schema change, look at the rendered page top to bottom before calling it done. *Tamim (15 May 2026): a stray character before the script tag printed text above the header.*
- **R076** `high` Check that the JSON-LD @graph names the client (knowledgegraph_name, website_name, logo and its _id, phones, address) and not a donor. *Ridgeline (12 Aug 2026): the <title> said Ridgeline while @graph still said Sunshine State Windows with the donor logo.*
- **R077** `high` On a multi-market site emit one LocalBusiness (trade type) per market with that market's NAP, on that market's pages only. *Elevation (Oct 2026): HousePainter per market via the ep-seo.php mu-plugin; a site-wide single NAP would put Colorado's phone on Florida pages.*
- **R078** `normal` Do not add a second schema source on top of an existing one; find and report every emitter (Rank Math, Elementor Custom Code snippets, mu-plugins, theme, GTM). *Elevation still carried Sunset's sitewide RoofingContractor snippet #7332 until it was drafted; ProWash's old schema blocked the new one.*
- **R079** `normal` On Elevation, change market schema through the build's seo layer (ep-seo.php), not Rank Math's per-page schema. *The HousePainter blocks are emitted by an mu-plugin pushed by seo.php; Rank Math schema on top would duplicate them.*
- **R080** `normal` On a rank-holding launch, keep the old schema identity as it was even where it disagrees with the new footer; fix it later as its own change. *Yard Dogs schema hours said Mon to Sun 9 to 5 while the footer said Mon to Fri 8 to 6; the rule was hold, don't fix.*
- **R081** `normal` Allow 24 hours or more for new schema to show in the validator before redoing anything. *Tamim (14 May 2026) on Sunset and Legacy local schema.*
- **R082** `normal` Check post_author and licence numbers in schema: a donor author slug or a licence with the wrong trade prefix is a leftover. *SunsetTamim123 leaked into /author/ in schema on Sunshine; a CCC (roofing) licence rode along on a window company (CBC building, CGC general).*

### FAQ (5)

- **R083** `high` Before editing a FAQ, find out if it is a global template (`[elementor-template id=9182]` or 2873) or a per-page accordion; editing the global changes every page that embeds it. *On the FSO templates the FAQ is one library template pulled in by shortcode; Tamim hit this on Legacy service pages (5 to 8 May 2026).*
- **R084** `high` Confirm an accordion is actually the FAQ before writing to it; the accordion under a hero is often an explainer. *Sunshine (Aug 2026): the under-hero explainer accordion was mapped as FAQ and clobbered, palette swatches included.*
- **R085** `high` Unique FAQs per page is the SEO goal, but turning a global FAQ into per-page FAQs is a structural change: escalate it. *Tamim and Beckett (4 May 2026): global FAQs across pages are bad for SEO; free sites ship one global FAQ and per-page FAQs come with the SEO upgrade.*
- **R086** `normal` Edit FAQ items in the accordion's repeater (`settings.tabs[i].tab_title` and `tab_content`), keeping item count and order unless asked. *Repeaters are invisible to sweeps written for title/editor (Ridgeline: service-page tabs kept impact-window copy).*
- **R087** `normal` Answer a question heading in the first sentence under it, and never name a service the client does not list or a price. *Beckett rulings on LCC (15 Sep 2026); Elevation answers cost as what drives the price, no number.*

### Content and copy (15)

- **R088** `blocker` Write by element id and field; never string-replace raw _elementor_data. *Elementor stores curly apostrophes escaped so phrases silently fail to match, and phrase maps converted half a sentence on Ridgeline ("... or a screen for the lanai" on a fence site).*
- **R089** `high` Replace whole paragraphs, not fragments of sentences, and swap longer strings before shorter ones. *"Replace" to "Security" turned "Window Replacement" into "Window Securityment"; a phrase swap ate a tag and printed "Fort Myers./span>".*
- **R090** `high` No em dashes in any copy you write; use a comma or a full stop. *House style; on rank-holding pages the em dash to comma swap is the one allowed edit to preserved paragraphs.*
- **R091** `high` Use US spelling on US sites (color, neighborhood, license, center, gray, aluminum). *WesCo shipped "neighbourhoods" and "kerb"; Elevation needed a US spelling pass on pages and templates (13 Oct 2026).*
- **R092** `high` Keep every ranking heading and the paragraphs under it word for word on a rank-holding site; only em dash to comma and Tamim-approved H1 edits are allowed. *Tamim's preserve rule (29 Sep 2026), used on Yard Dogs and Elevation.*
- **R093** `high` Every number, warranty, award or claim must trace to something the client said; never invent or carry one over. *Ridgeline launched claiming 6,400 projects this year (Sunset's number) for a company founded in January; Elevation's warranty is 7-year, not lifetime.*
- **R094** `high` If a field is bound to a dynamic tag (`__dynamic__`) or a global, writing the literal does nothing: change the source (esci_* option, ACF field) or remove the binding with Beckett's OK. *Yard Dogs contact boxes kept Sunshine's phone because a dynamic tag overrode the static text; buttons read "Get a Free Estimate" from esci_consultation_text.*
- **R095** `normal` Copy that a client named exactly ships exactly; put any concern in one line after it, never a substitute. *Beckett (5 Oct 2026): his specific words are the spec.*
- **R096** `normal` Remove placeholder or hidden text instead of hiding it with CSS. *Pax (22 Dec 2025) was flagged by Amazon after launch for lorem ipsum in hidden sections.*
- **R097** `normal` Find text printed by CSS `content:` in the raw HTML and change only the quoted string, leaving every other CSS declaration byte for byte. *Ridgeline printed "Serving Southwest Florida" via ::after; Dobbins card labels read "See landscaping" from CSS.*
- **R098** `normal` Treat sitewide text outside the main content (top bar, hidden tagline, footer NAP and hours, footer blurb) as ranking text too. *Beckett caught the "Volusia County and the Surrounding Areas" bar on Yard Dogs; the footer blurb is esci_footer_text, not Elementor.*
- **R099** `normal` Give each market, town or city page its own 150 to 300 word local paragraph; never repeat one paragraph across pages. *Tamim's thin-content rule (Elevation, 12 Oct 2026); many city pages from one template read as duplicate content.*
- **R100** `normal` Use one link format per field (relative path or full URL, not both), and check hard-coded card and button links: publishing a page does not fix them. *ProWash built a doubled URL (site/free-quote/https://site/free-quote/); Sunshine card links were hard-coded "#".*
- **R101** `normal` Never link to a parked or unlaunched page. *Elevation (Oct 2026): pages built but not launching sit in one parked set and nothing may link to them.*
- **R102** `normal` Phone links are always `tel:+1` followed by ten digits. *Ridgeline's tel:+4237798436 and Sunset's tel:+1:2399202414 looked right on screen and dialled nowhere.*

### Elementor data (8)

- **R103** `blocker` Store _elementor_data with `wp_slash(wp_json_encode($data))` and validate the JSON before writing. *Elementor stores the meta slashed; writing it unslashed corrupts the page, and Elevation's scripts stop on invalid JSON.*
- **R104** `high` Dump every string setting of the page, including repeater arrays (items, tabs, slides, cards), before planning a change. *Six of Ridgeline's misses were repeater arrays, each named differently, that a title/editor sweep never saw.*
- **R105** `high` Regenerate post_content after writing _elementor_data (regen-content.php). *post_content is a stale snapshot that site search, Rank Math meta and schema read; Dobbins search results showed donor text after a perfect fill (5 Oct 2026).*
- **R106** `high` Check globalTemplateID before assuming a section is shared: "global-looking" sections are often per-page copies that need every instance changed. *Sunshine's services cards were a per-page copy on 17 pages; editing the home page propagated nothing.*
- **R107** `high` On Legacy, Diamond and the OG template, service and city pages are ACF-driven (hero, sub-services, FAQ, workflow come from ACF fields); on the Sunshine-lineage FSO sites they live in _elementor_data. Edit the layer that renders. *Legacy's 73 service and city pages have zero page trees (one template #2254 + ACF); a Legacy hero imported empty because its copy is bound by ACF dynamic tags.*
- **R108** `normal` After a structured write, scan the post for duplicate element ids. *A dangling foreach-by-reference variable overwrote a heading on 6 pages with a "4." step marker; the duplicate-id scan caught it.*
- **R109** `normal` Do not rename menus, terms or page slugs as part of a copy edit: Elementor's nav widget references menus by slug and silently falls back to the first menu. *Ridgeline (12 Aug 2026): a menu rename left all three footer columns showing the same four links.*
- **R110** `normal` Some template sections are locked from the SEO editor or bound to fields; if a heading cannot be found in the page's own data, look in its template or ACF before concluding it is missing. *Cold Iron and the city-service template exposed only the hero, the next heading and the FAQ to the SEO team (Jun 2026).*

### Templates and globals (6)

- **R111** `blocker` Treat shared templates as site-wide edits: service areas 2478 (Sunset markets 6057, 6062, 6067, 6070), FAQ 9182 / 2873, header 14, footer 47, lead forms 9936 / 2535 / 2087; editing one changes every page that embeds it. *Beckett (23 Sep 2026): "you don't have to sweep 11 pages" for a string that lives in one template, and sweeping creates inconsistent copies.*
- **R112** `high` Theme-builder templates apply by condition (single service #2254, city-service #2677, single project #1347, project archive #1146, blog archive #1411, single post #1457): an edit lands on every page of that type. *The HHL template set is one master template applied site-wide on Sunset and Legacy.*
- **R113** `normal` On Sunset, 2873 (Global FAQ) and 7732 (why choose us) are source templates not linked from live pages; the live pages hold their own copies. *Sunset microsite work (14 Oct 2026) found pages carrying duplicated copies with the same widget ids.*
- **R114** `normal` Per-page strings still need a per-page edit: H1s and their spans, "Recent work across X" strips, excerpts, Rank Math fields, ACF fields and esci page overrides. *Global-templates rule (LCC, 23 Sep 2026): only the template-held blocks are edit-once.*
- **R115** `normal` Hide a header button with visibility:hidden, never display:none (escalate the CSS change). *Elevation (22 Oct 2026): display:none collapsed the flex row and slid the nav off-centre.*
- **R116** `normal` Keep unused template pages (city-service template, location template) in draft; never publish one. *A published city-service template page with excavation copy sat on a construction site until unpublished (7 May 2026).*

### Multi-market (microsite) sites (6)

- **R117** `high` On Sunset-style multi-market sites every page of a market must carry its own stamps (_market_nav_menu, _market_footer_menu_1..3, _esci_page_phone, _esci_page_phone_tel, _esci_page_email, _esci_page_location); there is no inheritance. *Sunset (14 Oct 2026): menus were stamped but contact only on home and contact pages, so 108 service, about and city pages showed Fort Myers' phone.*
- **R118** `high` Never put another market's phone, address, warranty or photos on a market page. *Elevation (Oct 2026): market tokens come from the page's market; lifetime warranty and Colorado exteriors never on Florida pages.*
- **R119** `normal` Know which chrome mechanism the site uses: Sunset = one header and footer plus per-page meta; Elevation = header and footer templates by URL section (display conditions). *Elevation chose display conditions so the market chrome cannot drift (13 Oct 2026); editing the wrong layer changes nothing.*
- **R120** `normal` Body-copy phone numbers and emails are plain text, not from the contact plugin: update them by hand and audit for leaks. *Sunset bug list item 8 (Oct 2026).*
- **R121** `normal` On Elevation the WordPress front page is the Colorado page and /colorado/ 301s to /. *Set at launch (22 Oct 2026) so the home keeps the old home page's 85 rankings.*
- **R122** `normal` Market service-area blocks are market-wide templates (one per market), not one global. *Beckett (4 May 2026): a single global would show the wrong cities on other markets.*

### Redirects, slugs, front page (5)

- **R123** `blocker` Resolve every page by its path, never by "the front page" (page_on_front), and never re-push a drafted page. *Elevation (22 Oct 2026): push.php resolved the brand-home row as page_on_front after / was switched to Colorado, overwrote Colorado with the drafted home and / went 404.*
- **R124** `blocker` Never add or re-add a redirect for /blog or /contact to its trailing-slash form; WordPress already adds the slash and Rank Math strips it, which loops. *Elevation (Oct 2026): /blog to /blog/ looped and the redirect was deleted (rm-blog-redirect.php); /contact was dropped for the same reason.*
- **R125** `high` Never change a slug yourself; if Beckett approves one, add a 301 from the old URL, keep _wp_old_slug, rewrite menu and breadcrumb links, and flush the sitemap cache. *Slug changes are URL changes; Ridgeline's /services-hub/ fix needed _wp_old_slug and link rewrites (12 Aug 2026).*
- **R126** `normal` Redirects live in Rank Math's redirections table; after editing them delete the rank_math_redirections_cache transient. *Elevation's redirect fix cleared the transient so the change took effect.*
- **R127** `normal` Keep existing URLs exactly and 301 every removed URL to its closest page. *Tamim's preserve rule; Elevation carried 30 redirects including old 2019 to 2021 WordPress URLs, junk URLs left 404.*

### Images (5)

- **R128** `normal` Alt text lives in two places, the widget's image.alt and the attachment's _wp_attachment_image_alt, and survives an image swap: set or clear both. *Ridgeline (12 Aug 2026) shipped 18 inline and 46 attachment alts describing palms and storm skies behind Tennessee fence photos.*
- **R129** `normal` A page's featured image is the og:image fallback even when the page never shows it. *Yard Dogs (30 Sep 2026): featured images were donor photos and showed in the iMessage preview.*
- **R130** `normal` Never AI-edit, upscale or restore a client's real photos; geotag with the tool and name folders by project type and city, never street address. *Standing rule on real photos; Tamim's geotag and folder method (May to Jun 2026).*
- **R131** `normal` The favicon is a PNG (512 square), never SVG or WebP, and Google takes days to show a new one. *Safari and iOS ignore SVG favicons; Google rejects WebP; Sunshine's favicon change took days (17 Aug 2026).*
- **R132** `normal` After replacing an SVG file, re-sync the attachment's _elementor_inline_svg meta. *Elementor inlines the meta, not the file; overwriting the .svg changed nothing twice in one day.*

### Legal pages (2)

- **R133** `high` Check privacy, terms and ADA pages for the client's own company name, phone (text and tel: link) and an email whose domain has MX; fix post_content as well as _elementor_data. *22 Sep 2026: four live privacy policies named Sunshine State Hurricane Protection and a dead email domain; LCC showed WesCo's phone with Ridgeline's tel: link; donor text survived in post_content on three sites.*
- **R134** `normal` Known open item: Bucktown's privacy page is unlinked and gives a dead-domain email (real: wade@bucktowngradingandconstruction.com) with two broken tel: links sitewide. *Blocked on the GHL key import (22 Sep 2026).*

### DNS and domains (4)

- **R135** `high` Never touch MX, SPF, DKIM, DMARC or _domainconnect records; DNS changes beyond a verification TXT are Beckett's. *Losing them sends the client's mail to spam silently (WesCo migration, Sep 2026).*
- **R136** `normal` Verify Search Console by a DNS TXT record (send the value to Claude, it is added in Cloudflare), not a WordPress meta tag. *Linking GSC to GA4 needs a verified owner; full GSC user access was not enough (13 May 2026); Elevation's handover uses DNS.*
- **R137** `normal` The canonical host is always www with trailing slashes; the apex 301s to www. *Beckett (9 Oct 2026): "when we do domains, it's always www" (Dobbins went apex by mistake).*
- **R138** `normal` If a site "isn't loading" right after a DNS change, check negative DNS cache before touching anything. *Cloudflare's SOA negative TTL is 30 minutes; checking in the same minute poisons your own resolver.*

### Forms (2)

- **R139** `high` Never edit form fields, recipients or webhooks; forms are the template's native Elementor forms and Beckett maps every webhook. *Yard Dogs forms posted into another client's GHL until rewired; a whole-page re-push nearly wiped mapped webhooks (30 Sep 2026).*
- **R140** `normal` Fact-gate the text inside form templates (9936, 2087, 2535) like any other copy. *Dobbins (5 Oct 2026): the contact form promised "We'll get back to you within 2 hours. Guaranteed." from the donor.*

## Sources

- `~/.claude/hooks/wp-write-guard.sh`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/MEMORY.md`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/feedback_domains_always_www.md`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/feedback_schema_script_tags_cli.md`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/feedback_varnish_purge_host_header.md`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/reference_client_sites_registry.md`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/reference_cloudflare_full_token.md`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/reference_ghl_hosting_cloudflare_inert.md`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/reference_ghl_wp_hide_blog_and_purge.md`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/reference_legacy_wp_access.md`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/reference_legal_pages_audit.md`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/reference_sunset_microsite_chrome.md`
- `~/.claude/projects/-Users-beckettcolee-claudecode-workspace/memory/reference_sunshine_wp_access.md`
- `~/.claude/skills/free-site-offer/SKILL.md`
- `~/.claude/skills/free-site-offer/references/content-swap.md`
- `~/.claude/skills/free-site-offer/references/done-gate.md`
- `~/.claude/skills/free-site-offer/references/launch.md`
- `~/.claude/skills/free-site-offer/references/misses-ledger.md`
- `~/.claude/skills/free-site-offer/references/seo-fso.md`
- `~/.claude/skills/free-site-offer/references/stress-calls.json`
- `~/.claude/skills/free-site-offer/references/stress-test.md`
- `~/.claude/skills/free-site-offer/scripts/purge.sh`
- `~/.claude/skills/native-wp-build/SKILL.md`
- `~/.claude/skills/native-wp-build/references/market-microsites.md`
- `~/.claude/skills/native-wp-build/references/rules-in-his-words.md`
- `~/.claude/skills/native-wp-build/research/01-mehedi-method.md`
- `~/.claude/skills/native-wp-build/research/01c-php-section-framework.md`
- `~/.claude/skills/native-wp-build/research/02-wp-feature-bank.md`
- `~/.claude/skills/native-wp-build/scripts/guard.php`
- `~/.claude/skills/wireframe-to-website/references/fix-ledger.md`
- `~/.claude/skills/wireframe-to-website/references/hhl-section-library.md`
- `~/.claude/skills/wireframe-to-website/references/site-audit.md`
- `~/.claude/skills/wireframe-to-website/references/wp-elementor-cli-fill.md`
- `~/claudecode-workspace/Client-Work/Elevation-Painting/site/DEV-NOTES.md`
- `~/claudecode-workspace/Client-Work/Elevation-Painting/site/MICROSITE-WP.md`
- `~/claudecode-workspace/Client-Work/Elevation-Painting/site/SEO-PRESERVE.md`
- `~/claudecode-workspace/Client-Work/Elevation-Painting/site/WHATS-LEFT.md`
- `~/claudecode-workspace/Client-Work/Elevation-Painting/site/launch/tamim-seo-handover.html`
- `~/claudecode-workspace/Client-Work/Elevation-Painting/site/wp/build/push.php`
- `~/claudecode-workspace/Client-Work/Elevation-Painting/site/wp/build/rm-blog-redirect.php`
- `~/claudecode-workspace/Client-Work/Elevation-Painting/site/wp/build/us-spelling-tpl.php`
