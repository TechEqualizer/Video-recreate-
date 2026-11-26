// Render index.html to an MP4 (video only) with optional motion blur.
//
//   node render.js out.mp4 [fps=60] [--sub 3] [--shutter 0.5] [--workers 3]
//   node render.js prefix 30 --stills t1,t2,...
//
// Motion blur: each output frame averages `sub` sub-frames spread across `shutter`
// of the frame interval (0.5 = 180-degree film shutter). sub=1 disables blur.
// Frames are split across `workers` browser pages, each encoding its own segment,
// then the segments are joined losslessly.
const { chromium } = require('playwright');
const { spawn, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const arg = (name, def) => { const i = process.argv.indexOf('--' + name); return i > 0 ? process.argv[i + 1] : def; };

async function openPage(browser) {
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(__dirname, 'index.html'));
  await p.evaluate(() => window.ready());
  return p;
}

async function renderSegment(browser, f0, f1, fps, sub, shutter, segPath) {
  const p = await openPage(browser);
  const inRate = fps * sub;
  const vf = sub > 1
    ? `tmix=frames=${sub},select='eq(mod(n\\,${sub})\\,${sub - 1})',setpts=N/(${fps}*TB)`
    : 'null';
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(inRate), '-c:v', 'mjpeg', '-i', '-',
    '-vf', vf, '-r', String(fps), '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', '-g', String(fps / 2), segPath],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = f0; f < f1; f++) {
    for (let k = 0; k < sub; k++) {
      const t = (f + (sub > 1 ? (k / (sub - 1) - 0.5) * shutter : 0)) / fps; // centred shutter
      await p.evaluate(t => seek(Math.max(0, t)), t);
      const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await p.close();
}

(async () => {
  const out = process.argv[2] || 'out.mp4';
  const fps = Number(process.argv[3]) || 60;
  const b = await chromium.launch();
  const stills = arg('stills');
  if (stills) {
    const p = await openPage(b);
    for (const t of stills.split(',').map(Number)) { await p.evaluate(t => seek(t), t); await p.screenshot({ path: `${out}_${t.toFixed(2)}.png` }); }
    await b.close(); return;
  }
  const sub = Number(arg('sub', 3)), shutter = Number(arg('shutter', 0.5)), workers = Number(arg('workers', 3));
  const p0 = await openPage(b);
  const dur = await p0.evaluate(() => window.DURATION), cuts = await p0.evaluate(() => window.CUTS);
  await p0.close();
  const n = Math.round(dur * fps);
  const per = Math.ceil(n / workers);
  const tmp = fs.mkdtempSync(path.join(path.dirname(path.resolve(out)), '.seg-'));
  const segs = [];
  const t0 = Date.now();
  await Promise.all(Array.from({ length: workers }, (_, w) => {
    const f0 = w * per, f1 = Math.min(n, f0 + per);
    const seg = path.join(tmp, `seg${w}.mp4`); segs.push(seg);
    return f0 < f1 ? renderSegment(b, f0, f1, fps, sub, shutter, seg) : null;
  }));
  fs.writeFileSync(path.join(tmp, 'list.txt'), segs.filter(fs.existsSync).map(s => `file '${s}'`).join('\n'));
  spawnSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', path.join(tmp, 'list.txt'), '-c', 'copy', out], { stdio: 'inherit' });
  segs.forEach(s => fs.existsSync(s) && fs.unlinkSync(s)); fs.unlinkSync(path.join(tmp, 'list.txt')); fs.rmdirSync(tmp);
  console.log(JSON.stringify({ out, frames: n, fps, sub, shutter, duration: dur, seconds: Math.round((Date.now() - t0) / 1000), cuts }));
  await b.close();
})();
