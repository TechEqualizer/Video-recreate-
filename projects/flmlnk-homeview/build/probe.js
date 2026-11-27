// Render named stills from a page and report errors + per-frame time: node probe.js page.html out_prefix t1,t2,...
const { chromium } = require('playwright');
(async () => {
  const [page, prefix, ts] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => console.log('PAGEERROR', e.message));
  p.on('console', m => { if (m.type() === 'error') console.log('CONSOLE', m.text()); });
  await p.goto('http://127.0.0.1:8765/' + page); await p.evaluate(() => window.ready());
  console.log('duration', await p.evaluate(() => window.DURATION));
  for (const t of ts.split(',').map(Number)) { const t0 = Date.now(); await p.evaluate(t => seek(t), t); await p.screenshot({ path: `${prefix}_${t.toFixed(2)}.png` }); console.log('t', t, 'ms', Date.now() - t0); }
  await b.close();
})();
