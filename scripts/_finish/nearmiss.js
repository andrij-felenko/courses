// НАЙВАЖЛИВІША перевірка: чи 18 «нових» тем math справді відсутні — чи вони Є під ІНШИМ slug?
// Якщо є синонім — правильна дія РЕТАРГЕТИТИ лінк, а НЕ заводити дубль (пастка asymptotic-notation).
const fs = require('fs');
const path = require('path');
const REPO = 'E:\\develop\\courses';

// усі теми math + де вони
const w = { __BOOKS__: [] };
new Function('window', fs.readFileSync(path.join(REPO, 'book', 'math', 'manifest.js'), 'utf8'))(w);
const ALL = [];
for (const s of w.__BOOKS__[0].sections || []) for (const t of s.topics || []) ALL.push({ slug: t.slug, title: t.title || '', section: s.slug, basic: t.basic && t.basic.status });

const NEW = ['chomsky-hierarchy','binary-decision-diagram','boolean-satisfiability','formal-language','godel-incompleteness','church-turing-thesis','zhegalkin-polynomial','mathematical-proof','natural-numbers','well-ordering-principle','signed-multiplication','prime-numbers','fibonacci-numbers','lcm','linear-diophantine','modular-inverse','fermat-little-theorem','multiplicative-order'];

// ручні синоніми-підказки укр/англ, щоб ловити не лише збіг токенів
const HINT = {
  'prime-numbers': ['prime', 'прост', 'решет', 'sieve', 'факториз', 'factoriz'],
  'natural-numbers': ['natural', 'натуральн', 'peano', 'пеано', 'числ'],
  'lcm': ['lcm', 'нск', 'кратн', 'multiple', 'gcd', 'нсд'],
  'modular-inverse': ['inverse', 'обернен', 'modular', 'модул'],
  'fermat-little-theorem': ['fermat', 'ферма'],
  'multiplicative-order': ['order', 'порядок', 'multiplicative', 'мультиплікат'],
  'fibonacci-numbers': ['fibonacci', 'фібоначч'],
  'linear-diophantine': ['diophantine', 'діофант', 'linear', 'рівнянн'],
  'signed-multiplication': ['multipl', 'множенн', 'booth', 'бут', 'signed', 'знаков'],
  'mathematical-proof': ['proof', 'доведенн', 'доказ'],
  'well-ordering-principle': ['order', 'впорядк', 'induction', 'індукц'],
  'church-turing-thesis': ['church', 'turing', 'тюринг', 'черч', 'обчислюв', 'computab'],
  'godel-incompleteness': ['godel', 'гедел', 'incomplete', 'неповнот'],
  'formal-language': ['language', 'мова', 'grammar', 'граматик', 'formal', 'формальн'],
  'chomsky-hierarchy': ['chomsky', 'хомськ', 'hierarchy', 'ієрарх', 'grammar', 'граматик'],
  'boolean-satisfiability': ['sat', 'satisf', 'здійсн', 'boolean', 'бул'],
  'binary-decision-diagram': ['bdd', 'decision', 'diagram', 'діаграм', 'рішен'],
  'zhegalkin-polynomial': ['zhegalkin', 'жегалк', 'polynom', 'полін', 'xor', 'reed', 'muller'],
};

for (const n of NEW) {
  const toks = n.split('-').filter(t => t.length > 2);
  const hints = HINT[n] || [];
  const hits = ALL.filter(t => {
    const hay = (t.slug + ' ' + t.title).toLowerCase();
    if (toks.some(tk => t.slug.includes(tk))) return true;
    return hints.some(h => hay.includes(h));
  });
  console.log(`\n■ ${n}`);
  if (!hits.length) { console.log('    → збігів НЕМА: тема справді відсутня, заводити нову ✔'); continue; }
  for (const h of hits) console.log(`    ? ${h.section}/${h.slug}  [${h.basic}]  «${h.title}»`);
}
