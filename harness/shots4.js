const { open } = require('./common');
(async () => {
  const out = '/home/claude/agenthq/assets/';
  const t = await open({ swarm: 'big' }); const p = t.page;
  await p.click('#zoom'); await p.waitForTimeout(700);
  await p.screenshot({ path: out + 'c1.png' });
  await p.evaluate(() => __stall('big', 'legal', { name: 'Legal', order: 11, role: 'Contract reader', model: 'Opus 5.5', status: 'working', statusAt: '2026-11-01T00:00:00Z', task: 'Read the terms.', look: { awning: ['#2f6f5e', '#f6e7c8'], panel: '#2f6f5e', goods: 'boba', acc: ['glasses'] } }));
  await p.evaluate(() => __stall('big', 'pricing', { name: 'Pricing', order: 12, role: 'Analyst', model: 'Sonnet 5.5', status: 'working', statusAt: '2026-11-01T00:00:00Z', task: 'Model three price points.' }));
  await p.waitForTimeout(900);
  await p.screenshot({ path: out + 'c2.png' });
  console.log('errors', t.errs.slice(0, 5)); await t.close();
})();
