// Print the timeline's exact cuts as JSON: node cuts.js > out.cuts.json
const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.resolve(__dirname, 'index.html'));
  console.log(JSON.stringify({ duration: await p.evaluate(() => DURATION), cuts: await p.evaluate(() => CUTS) })); await b.close(); })();
