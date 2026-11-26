// Render index.html frame by frame to an MP4 (video only).
// Usage: node render.js out.mp4 [fps] [--stills t1,t2,...]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

(async () => {
  const out = process.argv[2] || 'out.mp4';
  const fps = Number(process.argv[3]) || 30;
  const stillsArg = process.argv.indexOf('--stills');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(__dirname, 'index.html'));
  await p.evaluate(() => window.ready());
  const dur = await p.evaluate(() => window.DURATION);
  if (stillsArg > 0) {
    const ts = process.argv[stillsArg + 1].split(',').map(Number);
    for (const t of ts) { await p.evaluate(t => seek(t), t); await p.screenshot({ path: `${out}_${t.toFixed(2)}.png` }); }
    await b.close(); return;
  }
  const n = Math.round(dur * fps);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-g', '15', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < n; f++) {
    await p.evaluate(t => seek(t), f / fps);
    const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.error(`frame ${f}/${n}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  console.log(JSON.stringify({ out, frames: n, duration: dur, cuts: await p.evaluate(() => window.CUTS) }));
  await b.close();
})();
