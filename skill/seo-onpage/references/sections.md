# Sections: how our sites are put together, and how to talk about them

## One template family
Almost every HHL site is built from one Elementor template family (it started as the Sunset / Legacy "Aarmor" build;
Sunshine, WesCo, Elevation and most FSO sites are copies of it). So the same section types and the same shared
template ids show up on site after site. `seo audit <site>` writes the real map for each client
(`~/.seo-onpage/sites/<site>/SECTION-MAP.html` + `section-map.json`); read it before talking about a site.

## Saying which section you mean
Any of these work, the skill resolves them against section-map.json:
- page + type: "the FAQ on florida interior", "the why-us on the Colorado home"
- page + number: "section 4 on /florida/interior-painting/"
- page + its heading: "the 'Every painting job, one careful crew' section on castle rock"
If two sections match, ask which one (show both names + their screenshots).

## Section types you'll see (in the usual order on a page)
| Type | What it is | SEO fields in it |
|---|---|---|
| Hero | the top: kicker, H1 (or the big line), intro, buttons | H1, intro paragraph |
| Services | cards or a toggle of the services, each with a short line | H2 + H3 per card |
| Explainer / sub-services | "What X includes", accordions or icon boxes | H2, H3s or accordion titles |
| Process / steps | 3 or 4 numbered steps | H2, step titles (the "1." "2." numbers are decoration) |
| Projects / gallery | recent projects grid (pulled from project posts) | H2 only; cards are the projects' own titles |
| Call to action | mid-page band with a question + buttons | H2 |
| Why us | reasons, icon boxes | H2 + H3 per reason |
| Team / about | people, story | H2s |
| FAQ | accordion of questions | H2 + each question/answer |
| Service areas | "Serving ..." with county / town toggles | **shared template**: H2 + area names |
| Header / footer | nav, phone, address | **shared**, never edited by the kit |

## Shared (global) templates: every edit changes every page that uses them
| Id | What | Used on |
|---|---|---|
| 14 / 47 | Header / footer | every page: not editable with the kit |
| 2478, 6070, 6067 (+ 6057, 6062 on Sunset) | Service areas ("Serving ...") per market | every page in that market |
| 9182 / 2873 | Global FAQ (on sites that use one) | every page that embeds it |
| 2254 / 2677 | Single service / city-service template (Sunset-style CPT sites) | every service / city page |
| 1457 / 1347 | Single blog post / single project | every post / project |
| 1411 / 1146 | Blog archive / project archive | /blog/ and /projects/ only |
| 9936 / 2535 / 2087, 10343-10355 (Elevation) | Forms | contact / careers pages: never edit with the kit |
The plan marks any row in these as `global` and lists the pages it reaches.

## What is per page (safe to edit page by page)
Hero, page-specific H2s, explainers, why-us, process step titles, page FAQ accordions, meta. On microsite sites
(Elevation, Sunset) the market's phone, nav and footer menus are set per page by plugins: never edit those fields.
