// Rendu image par image de index.html (Chromium headless) puis encodage ffmpeg.
//   node render.js stills out/stills 1.5 6.2 11.2 ...   -> PNG aux instants donnés
//   node render.js video out/video.mp4 [workers]       -> vidéo muette 30 s / 30 i/s
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30, DUR = 30, FRAMES = FPS * DUR;
const PAGE = 'file://' + path.resolve(__dirname, 'index.html') + '?render';

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto(PAGE);
  await page.evaluate(() => window.ready);
  return page;
}

async function stills(outDir, times) {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await openPage(browser);
  for (const t of times) {
    await page.evaluate(t => renderAt(t), t);
    await page.screenshot({ path: path.join(outDir, `t${t.toFixed(2).padStart(5, '0')}.png`) });
  }
  await browser.close();
}

async function renderRange(browser, from, to, file) {
  const page = await openPage(browser);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-pix_fmt', 'yuv420p', '-r', String(FPS), file], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = from; f < to; f++) {
    await page.evaluate(t => renderAt(t), f / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 96 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - from) % 30 === 0) console.log(`  ${path.basename(file)} : image ${f}/${to}`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg ' + c))));
  await page.close();
}

async function video(out, workers) {
  const tmp = path.join(path.dirname(out), 'segments');
  fs.mkdirSync(tmp, { recursive: true });
  const per = Math.ceil(FRAMES / workers), jobs = [], list = [];
  for (let w = 0; w < workers; w++) {
    const from = w * per, to = Math.min(FRAMES, from + per), file = path.join(tmp, `seg${w}.mp4`);
    list.push(`file '${path.resolve(file)}'`);
    jobs.push((async () => { const b = await chromium.launch(); await renderRange(b, from, to, file); await b.close(); })());
  }
  await Promise.all(jobs);
  fs.writeFileSync(path.join(tmp, 'list.txt'), list.join('\n'));
  await new Promise((res, rej) => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(tmp, 'list.txt'), '-c', 'copy', out], { stdio: 'inherit' })
    .on('close', c => c === 0 ? res() : rej(new Error('concat ' + c))));
  fs.rmSync(tmp, { recursive: true, force: true });
}

const [mode, out, ...rest] = process.argv.slice(2);
(mode === 'stills' ? stills(out, rest.map(Number)) : video(out, Number(rest[0] || 4)))
  .catch(e => { console.error(e); process.exit(1); });
