const fs = require('fs');
const path = require('path');

const targetDir = 'E:/develop/courses/book/algorithms/data-structures/sorting-networks';

function proseWords(md) {
  let inCode = false, words = 0, figs = 0;
  for (let line of md.split(/\r?\n/)) {
    const t = line.trim();
    if (/^```/.test(t)) { inCode = !inCode; continue; }
    if (inCode) continue;
    if (/^!\[/.test(t)) { figs++; continue; }
    if (/^#{1,6}\s/.test(t)) line = t.replace(/^#{1,6}\s/, "");
    if (/^\|.*\|/.test(t)) continue;
    let s = line
      .replace(/`[^`]*`/g, " ")
      .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
      .replace(/\[[^\]]*\]\([^)]*\)/g, (m) => m.replace(/\]\([^)]*\)/, "").replace(/^\[/, ""))
      .replace(/^>\s*/, "").replace(/^[-*]\s+/, "").replace(/[*_#>`~]/g, " ");
    const m = s.match(/[\p{L}\p{N}’'\-]+/gu);
    if (m) words += m.length;
  }
  return { words, figs };
}

const files = fs.readdirSync(targetDir).filter(f => f.endsWith('.md'));
for (const f of files) {
  const content = fs.readFileSync(path.join(targetDir, f), 'utf8');
  const stats = proseWords(content);
  console.log(`${f}: ${stats.words} words, ${stats.figs} figures`);
}
