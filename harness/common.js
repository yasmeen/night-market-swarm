const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), http = require('http');
const ROOT = '' + require('path').join(__dirname, '..', 'page') + '';
const F = n => fs.readFileSync(path.join(__dirname, 'node_modules/@fontsource', n));
const CSS = `@font-face{font-family:'Silkscreen';src:url(https://fonts.gstatic.com/sk.woff2) format('woff2');}
@font-face{font-family:'Pixelify Sans';font-weight:400;src:url(https://fonts.gstatic.com/p4.woff2) format('woff2');}
@font-face{font-family:'Pixelify Sans';font-weight:600;src:url(https://fonts.gstatic.com/p6.woff2) format('woff2');}`;
const mk = (name, sprite, order, status, role, model, task) => ({ name, sprite, order, status, role, model, task, statusAt: '2026-11-01T00:00:00Z' });
const BASE = {
  orders: mk('Orders', 'orders', 0, 'working', 'Lead', 'Fable 5.2', 'Take the order, hire the crew, check the work.'),
  security: mk('Security', 'security', 1, 'done', 'Security auditor', 'Opus 5.5', 'Look for holes before anything ships.'),
  design: mk('Design', 'design', 2, 'working', 'Designer', 'Sonnet 5.5', 'Rework the landing page layout.'),
  seo: mk('SEO', 'seo', 3, 'working', 'SEO specialist', 'Haiku 5.5', 'Check titles, sitemap and page structure.'),
  code: mk('Code', 'code', 4, 'working', 'Builder', 'Sonnet 5.5', 'Build the new sign-up flow.'),
  backlog: Object.assign(mk('Backlog', 'backlog', 5, 'working', 'PR reviewers', 'Sonnet 5.5', 'Review every open pull request, one agent per PR.'), { crew: 8, total: 24 }),
  review: mk('Review', 'review', 6, 'idle', 'Reviewer', 'Opus 5.5', 'Opens when the builds are in.'),
};
const MORE = {
  docs: mk('Docs', 'docs', 7, 'working', 'Writer', 'Haiku 5.5', 'Write the setup guide.'),
  research: mk('Research', 'research', 8, 'working', 'Researcher', 'Sonnet 5.5', 'Compare three payment providers.'),
  marketing: mk('Marketing', 'marketing', 9, 'needs_you', 'Marketer', 'Sonnet 5.5', 'Draft the launch post.'),
  data: mk('Data', 'data', 10, 'working', 'Analyst', 'Sonnet 5.5', 'Chart last month of sign-ups.'),
};
const DONE = Object.fromEntries(Array.from({ length: 9 }, (_, i) => ['backlog-d' + i, { stall: 'backlog', worker: 'w' + (i % 8 + 1), unit: 'pr-' + i, done: true, at: '2026-11-01T00:0' + i + ':30Z', text: 'PR ' + (101 + i) + ' reviewed.' }]));
const EV = { ...DONE, 'design-01': { stall: 'design', at: '2026-11-01T00:01:00Z', text: 'Hero section is drafted. Moving on to the pricing cards.' }, 'code-01': { stall: 'code', at: '2026-11-01T00:02:00Z', text: 'Sign-up form is wired up. Writing tests next.' } };
const EV0 = EV;
const DATA = {
  swarms: { demo: { project: 'Night Market', job: 'Small', demo: true, createdAt: '2026-11-03' }, big: { project: 'Night Market', job: 'Demo', createdAt: '2026-11-02' } },
  stalls: { demo: BASE, big: { ...BASE, ...MORE } },
  events: { demo: { ...EV }, big: { ...EV } },
};
const INIT = `(${function (DATA) {
  window.__data = DATA; const subs = [];
  const snap = p => { const a = p.split('/'); const o = a.length === 1 ? DATA.swarms : ((DATA[a[2]] || {})[a[1]] || {}); return { docs: Object.entries(o).map(([id, d]) => ({ id, data: () => d })), metadata: { fromCache: false } }; };
  const db = { collection: p => ({ onSnapshot(cb) { subs.push([p, cb]); setTimeout(() => cb(snap(p)), 30); return () => {}; } }) };
  window.__stall = (sid, id, doc) => { DATA.stalls[sid][id] = doc; subs.filter(s => s[0] === 'swarms/' + sid + '/stalls').forEach(s => s[1](snap(s[0]))); };
  window.__push = (sid, id, ev) => { DATA.events[sid][id] = ev; subs.filter(s => s[0] === 'swarms/' + sid + '/events').forEach(s => s[1](snap(s[0]))); };
  window.claude = { use: async n => n === 'db' ? db : null };
}.toString()})(${JSON.stringify(DATA)})`;
async function open(opts = {}) {
  const server = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0].split('#')[0])); fs.readFile(f.endsWith('/') ? f + 'index.html' : f, (e, b) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'content-type': f.endsWith('.png') ? 'image/png' : 'text/html' }); r.end(b); } }); });
  await new Promise(ok => server.listen(0, ok));
  const port = server.address().port;
  const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ viewport: opts.viewport || { width: 1200, height: 675 }, deviceScaleFactor: 1, ...(opts.video ? { recordVideo: { dir: opts.video, size: opts.viewport || { width: 1200, height: 675 } } } : {}) });
  await ctx.route('https://fonts.googleapis.com/**', r => r.fulfill({ contentType: 'text/css', body: CSS }));
  await ctx.route('https://fonts.gstatic.com/**', r => { const u = r.request().url(); r.fulfill({ contentType: 'font/woff2', body: u.includes('sk') ? F('silkscreen/files/silkscreen-latin-400-normal.woff2') : F('pixelify-sans/files/pixelify-sans-latin-' + (u.includes('p6') ? '600' : '400') + '-normal.woff2') }); });
  await ctx.addInitScript(INIT);
  const page = await ctx.newPage();
  const errs = []; page.on('pageerror', e => errs.push(String(e))); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto(`http://localhost:${port}/index.html#${opts.swarm || 'demo'}`);
  await page.waitForTimeout(1200);
  return { page, ctx, browser, server, errs, close: async () => { await ctx.close(); await browser.close(); server.close(); } };
}
module.exports = { open };
