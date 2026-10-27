// Measure every heading a plan touches, on the rendered page, at phone (390) and desktop (1440) width.
//   node snapshot.cjs <plan.json> <base-url> <out.json> before|after
// before: finds each heading by its CURRENT text; after: by its NEW text. Records tag, font-size, and whether it is visible.
// verify.py compares the two: same size (unless the plan wanted it), text present, tag as planned.
const { chromium } = require(process.env.PLAYWRIGHT || [process.env.HOME + '/.seo-onpage/node/node_modules/playwright', process.env.HOME + '/.claude/skills/monthly-seo-report/node_modules/playwright'].find(p => require('fs').existsSync(p)));
const fs = require('fs');
const [planF, base, outF, phase] = process.argv.slice(2);
const plan = JSON.parse(fs.readFileSync(planF));
const rows = plan.map((x, i) => ({ ...x, i })).filter(x => (x.status === 'ready' || x.status === 'global') && (x.op === 'heading' || x.op === 'faq' || x.op === 'faq_add'));
const byPath = {}; rows.forEach(r => (byPath[r.path] = byPath[r.path] || []).push(r));
const norm = t => (t || '').toLowerCase().replace(/&/g, ' and ').replace(/\+/g, ' and ').replace(/[’'`]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
(async () => {
  const b = await chromium.launch(); const out = {};
  for (const [w, h] of [[390, 844], [1440, 900]]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h } }); const p = await ctx.newPage();
    for (const [path, rs] of Object.entries(byPath)) {
      await p.goto(base.replace(/\/$/, '') + path + (path.includes('?') ? '&' : '?') + 'nocache=' + Date.now(), { waitUntil: 'load', timeout: 90000 }).catch(() => {});
      await p.waitForTimeout(800);
      // entrance animations only reveal on scroll: walk the page so every section is rendered before measuring
      await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); });
      await p.waitForTimeout(600);
      const want = rs.map(r => ({ i: r.i, text: norm(phase === 'before' ? (r.now || r.new) : r.new), faq: r.op !== 'heading' }));
      const found = await p.evaluate((want) => {
        const norm = t => (t || '').toLowerCase().replace(/&/g, ' and ').replace(/\+/g, ' and ').replace(/[’'`]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
        const els = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,summary,.e-n-accordion-item-title-text,.elementor-tab-title,.elementor-icon-box-title,div,span,a')];
        return want.map(x => {
          const e = els.find(e => e.children.length < 4 && norm(e.textContent) === x.text) || els.find(e => e.children.length < 4 && x.text && norm(e.textContent).startsWith(x.text));
          if (!e) return { i: x.i, found: false };
          const h = e.closest('h1,h2,h3,h4,h5,h6') || e; const cs = getComputedStyle(h);
          return { i: x.i, found: true, visible: h.getBoundingClientRect().height > 0 && cs.display !== 'none', tag: h.tagName.toLowerCase(), h: Math.round(h.getBoundingClientRect().height), size: parseFloat(cs.fontSize), weight: cs.fontWeight };
        });
      }, want);
      for (const f of found) { out[f.i] = out[f.i] || {}; out[f.i][w] = f; }
    }
    await ctx.close();
  }
  fs.writeFileSync(outF, JSON.stringify({ phase, base, rows: out }, null, 1));
  const miss = Object.values(out).filter(v => !v[1440]?.found).length;
  console.log(`${phase}: ${Object.keys(out).length} rows measured, ${miss} not found at 1440`);
  await b.close();
})();
