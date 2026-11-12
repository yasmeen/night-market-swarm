const { open } = require('./common');
const fs = require('fs');
(async () => {
  const dir = '/home/claude/agenthq/harness/video';
  fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir);
  const t = await open({ swarm: 'big' });
  const p = t.page, w = ms => p.waitForTimeout(ms);
  // video-only overlays: a title card and captions. These are not part of the product page.
  await p.addStyleTag({ content: `
    #vcap { position: fixed; z-index: 9000; left: 50%; top: 74px; transform: translateX(-50%); padding: 10px 18px; background: #faf0d6; color: #0e0c1a; border: 4px solid #0e0c1a; border-radius: 6px; box-shadow: 5px 5px 0 #0e0c1a; font: 26px 'Silkscreen', monospace; white-space: nowrap; opacity: 0; transition: opacity .25s steps(4); pointer-events: none; }
    #vcap.on { opacity: 1; }
    #vtitle { position: fixed; z-index: 9500; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px; background: rgba(20, 16, 44, .78); opacity: 0; transition: opacity .45s steps(6); pointer-events: none; }
    #vtitle.on { opacity: 1; }
    #vtitle b { font: 400 84px 'Silkscreen', monospace; color: #fcd67c; text-shadow: 6px 6px 0 #0e0c1a; letter-spacing: 2px; }
    #vtitle span { font: 30px 'Pixelify Sans', sans-serif; color: #faf0d6; }
    #vtitle i { font: normal 20px 'Silkscreen', monospace; color: #f47864; }` });
  await p.evaluate(() => {
    const c = document.createElement('div'); c.id = 'vcap'; document.body.appendChild(c);
    const t = document.createElement('div'); t.id = 'vtitle'; t.innerHTML = '<i></i><b></b><span></span>'; document.body.appendChild(t);
    window.__cap = s => { c.textContent = s || ''; c.classList.toggle('on', !!s); };
    window.__title = (k, a, b) => { t.children[0].textContent = k || ''; t.children[1].textContent = a || ''; t.children[2].textContent = b || ''; t.classList.toggle('on', !!a); };
    __title('AI agent swarms, but make it a', 'Night Market', 'Every agent gets a booth. You get to walk around.');
  });
  const cap = s => p.evaluate(s => __cap(s), s);
  const push = (id, ev) => p.evaluate(([id, ev]) => __push('big', id, ev), [id, ev]);
  const stall = async name => { const b = await p.locator('.stall', { hasText: name }).first().boundingBox(); await p.mouse.click(b.x + b.width / 2, b.y + b.height * 0.75); };
  const park = () => p.mouse.move(70, 30);
  const done = i => push('backlog-d' + i, { stall: 'backlog', worker: 'w' + (i % 8 + 1), unit: 'pr-' + i, done: true, at: '2026-11-01T00:' + (10 + i) + ':00Z', text: 'PR ' + (101 + i) + ' reviewed. Safe to merge.' });
  await w(500);
  const cdp = await t.ctx.newCDPSession(p); const frames = [];
  cdp.on('Page.screencastFrame', f => { frames.push(f.metadata.timestamp); fs.writeFileSync(dir + '/f' + String(frames.length - 1).padStart(5, '0') + '.png', Buffer.from(f.data, 'base64')); cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {}); });
  await cdp.send('Page.startScreencast', { format: 'png', everyNthFrame: 2 });
  await park(); await w(2600);
  await p.evaluate(() => __title()); await w(500);

  await cap('Every booth is a job');
  await p.keyboard.down('ArrowUp'); await w(350); await p.keyboard.up('ArrowUp');
  await push('code-02', { stall: 'code', at: '2026-11-01T00:30:00Z', text: 'Tests pass. Opening the pull request.' }); await w(700);
  await push('design-02', { stall: 'design', at: '2026-11-01T00:31:00Z', text: 'Pricing cards are done. Looks sharp.' });
  await p.keyboard.down('ArrowLeft'); await w(1300); await p.keyboard.up('ArrowLeft'); await w(700);

  await cap('Lit means working. Vendors shout their updates.');
  await push('seo-02', { stall: 'seo', at: '2026-11-01T00:32:00Z', text: 'Sitemap fixed. 14 titles rewritten.' });
  await p.keyboard.down('ArrowRight'); await w(1500); await p.keyboard.up('ArrowRight'); await w(900);

  await cap('Big job? One booth runs a whole team.');
  await stall('Backlog'); await park(); await w(1500);
  for (const i of [9, 10, 11, 12, 13]) { await done(i); await w(650); }
  await w(900);
  await p.keyboard.press('Escape'); await w(200);

  await cap('Hire another agent and a new booth opens');
  await p.keyboard.down('ArrowDown'); await w(1500); await p.keyboard.up('ArrowDown');
  await p.keyboard.down('ArrowRight'); await w(1300); await p.keyboard.up('ArrowRight');
  const mk = (name, order, role, model, task, look) => ({ name, order, role, model, task, look, status: 'working', statusAt: '2026-11-01T00:00:00Z' });
  await p.evaluate(d => __stall('big', 'legal', d), mk('Legal', 11, 'Contract reader', 'Opus 5.5', 'Read the vendor terms for anything risky.', { awning: ['#2f6f5e', '#f6e7c8'], panel: '#2f6f5e', goods: 'boba', acc: ['glasses'] })); await w(800);
  await p.evaluate(d => __stall('big', 'pricing', d), mk('Pricing', 12, 'Analyst', 'Sonnet 5.5', 'Model three price points.')); await w(800);
  await p.evaluate(d => __stall('big', 'support', d), mk('Support', 13, 'Inbox triage', 'Haiku 5.5', 'Sort this week of support email.', { awning: ['#e0786e', '#fcf0d6', '#f4cc60', '#fcf0d6'], panel: '#e0786e', goods: 'fruit', acc: ['straw'] })); await w(800);
  await p.evaluate(d => __stall('big', 'growth', d), mk('Growth', 14, 'Experiment runner', 'Sonnet 5.5', 'Draft three landing page tests.')); await w(1100);

  await cap('Click any booth to see what it is doing');
  await push('legal-01', { stall: 'legal', at: '2026-11-01T00:40:00Z', text: 'Two clauses need a second look.' });
  await stall('Legal'); await park(); await w(2600);
  await p.keyboard.press('Escape'); await w(200);

  const cat = await p.locator('button[aria-label="Pet the cat"]').boundingBox();
  const dog = await p.locator('button[aria-label="Pet the dog"]').boundingBox();
  const pet = [cat, dog].find(b => b && b.x > 40 && b.x < 1120 && b.y > 130 && b.y < 620);
  if (pet) { await cap('Yes, you can pet the ' + (pet === cat ? 'cat' : 'dog')); for (let k = 0; k < 3; k++) { await p.mouse.click(pet.x + pet.width / 2, pet.y + pet.height / 2); await w(450); } await park(); await w(500); }

  await cap('Your whole swarm on one street');
  await p.click('#zoom'); await park(); await w(900);
  await push('marketing-02', { stall: 'marketing', at: '2026-11-01T00:41:00Z', text: 'Launch post is ready for you.' }); await w(600);
  await done(14); await w(500); await done(15); await w(1500);
  await cap('');
  await p.evaluate(() => __title('', 'Night Market', 'A walkable home for your AI agents')); await w(3000);
  await cdp.send('Page.stopScreencast');
  let list = '';
  for (let i = 0; i < frames.length; i++) list += `file 'f${String(i).padStart(5, '0')}.png'\nduration ${(i + 1 < frames.length ? frames[i + 1] - frames[i] : 0.08).toFixed(4)}\n`;
  fs.writeFileSync(dir + '/list.txt', list);
  console.log('frames', frames.length, 'secs', (frames[frames.length - 1] - frames[0]).toFixed(1), 'pet', !!pet, 'errors', t.errs);
  await t.close();
})();
