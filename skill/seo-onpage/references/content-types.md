# Projects and blog posts on our sites (how they're built, what you can change today)

This is understanding, not a workflow. Writing and publishing new posts is a later tool; don't improvise one.

## How they're built
- **Blog posts**: WordPress posts. Each post's page is drawn by one shared Elementor **single post template**; the blog
  page (`/blog/`) by one shared **archive template**. The post's title is the H1 (a dynamic field), the body is the post
  content. Rank Math SEO title, description and focus keyword live on each post.
- **Projects**: a custom post type (`project`). Same pattern: one **single project template** draws every project page
  (title = H1, gallery, details from custom fields), one **project archive template** draws `/projects/`. The archive's
  SEO title/description live in Rank Math's settings (not on a page), the tool handles that.
- Because the templates are shared, a heading INSIDE a template (e.g. "Recent work" on every project page) is a global
  change: the plan marks it `global`.

## What you can change today with the normal doc
- A project's or post's **title** (= its H1), **meta title**, **meta description**, **focus keyword**: one table per
  post URL, exactly like a page.
- The blog page and projects page **H1/H2 and meta**: the plan routes them to the archive template / Rank Math settings.

## Not yet (ask Beckett)
- New posts, new projects, images, galleries, categories, internal-link campaigns, blog content plans, schema per post.
  These are the "SEO blog" and "project posts" tools we'll build next.
