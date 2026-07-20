// v6-канон на 65 нових статтях: <preknowlist> під H1 + фігури/figs.py + вставки.
const fs = require('fs');
const path = require('path');
const REPO = 'E:\\develop\\courses';
const PAY = __dirname;   // payload-*.json лежать поруч, у scripts/_finish/
const BOOKS = ['communications', 'algorithms', 'programming', 'math', 'electronics'];

const rows = [];
let tot = { n: 0, pk: 0, fig: 0, figpy: 0, imgmiss: 0 };
const missPk = [], missImg = [];

for (const book of BOOKS) {
  const p = JSON.parse(fs.readFileSync(path.join(PAY, `payload-${book}.json`), 'utf8'));
  let n = 0, pk = 0, fig = 0, figpy = 0;
  for (const u of p.units) {
    const dir = path.join(REPO, 'book', book, u.section, u.slug);
    const f = path.join(dir, u.slug + '.md');
    if (!fs.existsSync(f)) { console.log('НЕМА ФАЙЛА:', f); continue; }
    n++;
    const src = fs.readFileSync(f, 'utf8');
    if (src.includes('<preknowlist>')) pk++; else missPk.push(`${book}/${u.slug}`);
    // фігури: чи є img-посилання і чи є генератор
    const imgs = [...src.matchAll(/!\[[^\]]*\]\(([^)]+\.svg)\)/g)].map(m => m[1]);
    if (imgs.length) {
      fig++;
      if (fs.existsSync(path.join(dir, 'figs.py'))) figpy++;
      for (const im of imgs) {
        const abs = im.startsWith('/') ? path.join(REPO, im.slice(1)) : path.join(dir, im);
        if (!fs.existsSync(abs)) missImg.push(`${book}/${u.slug}: ${im}`);
      }
    }
  }
  rows.push([book, n, pk, fig, figpy]);
  tot.n += n; tot.pk += pk; tot.fig += fig; tot.figpy += figpy;
}

console.log('книга           статей  preknow  зі SVG  є figs.py');
for (const [b, n, pk, fig, figpy] of rows)
  console.log(b.padEnd(15) + String(n).padStart(5) + String(pk).padStart(8) + String(fig).padStart(8) + String(figpy).padStart(9));
console.log('РАЗОМ'.padEnd(15) + String(tot.n).padStart(5) + String(tot.pk).padStart(8) + String(tot.fig).padStart(8) + String(tot.figpy).padStart(9));

console.log('\nБЕЗ <preknowlist> (' + missPk.length + '):');
missPk.forEach(x => console.log('  ' + x));
console.log('\nБИТІ SVG (' + missImg.length + '):');
missImg.forEach(x => console.log('  ' + x));
