// Screenshot every section of every page in section-map.json (desktop 1440). Saves shots/<page>-<n>.jpg
const { chromium } = require(process.env.PLAYWRIGHT || [process.env.HOME + '/.seo-onpage/node/node_modules/playwright', process.env.HOME + '/.claude/skills/monthly-seo-report/node_modules/playwright'].find(p => require('fs').existsSync(p)));
const fs = require('fs'); const path = require('path');
const [mapF, base, outDir] = process.argv.slice(2); const pages = JSON.parse(fs.readFileSync(mapF));
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage(); let n = 0;
  for (const pg of pages) {
    await p.goto(base.replace(/\/$/, '') + pg.path, { waitUntil: 'load', timeout: 90000 }).catch(() => {});
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 50)); } window.scrollTo(0, 0); });
    await p.waitForTimeout(500);
    const slug = pg.path.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').toLowerCase() || 'home';
    for (const s of pg.sections) {
      const el = p.locator(`.elementor-element-${s.id}`).first();
      if (await el.count()) { await el.screenshot({ path: path.join(outDir, `${slug}-${s.n}.jpg`), type: 'jpeg', quality: 55, timeout: 8000 }).catch(() => {}); n++; }
    }
  }
  console.log(`${n} section shots`); await b.close();
})();
