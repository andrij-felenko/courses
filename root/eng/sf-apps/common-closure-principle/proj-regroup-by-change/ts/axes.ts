// tools/axes.ts — осі зміни: які файли історія вперто міняє разом
import { execFileSync } from 'node:child_process';

const WINDOW = '18 months ago';  // осі старші за півтора року вже не ті
const MAX_FILES = 8;             // ширший коміт — це рефактор, а не «одна причина»
const MIN_SUPPORT = 3;           // рідше — випадковий збіг
const MIN_STRENGTH = 0.4;        // частка спільних комітів (Жаккар)

function history(): string[][] {
  const raw = execFileSync('git', [
    'log', `--since=${WINDOW}`, '--no-merges', '-M',
    '--name-only', '--pretty=format:%x00',
  ], { encoding: 'utf8', maxBuffer: 1 << 26 });

  return raw.split('\0')
    .map(block => [...new Set(block.split('\n').filter(l => /^src\/.+\.tsx?$/.test(l)))].sort())
    .filter(files => files.length > 1 && files.length <= MAX_FILES);
}

/** total: файл → скільки разів мінявся; pair: пара → скільки разів разом */
function coChange(commits: string[][]) {
  const total = new Map<string, number>();
  const pair = new Map<string, number>();

  for (const files of commits) {
    for (const f of files) total.set(f, (total.get(f) ?? 0) + 1);
    for (let i = 0; i < files.length; i++)
      for (let j = i + 1; j < files.length; j++) {
        const k = `${files[i]}\0${files[j]}`;
        pair.set(k, (pair.get(k) ?? 0) + 1);
      }
  }
  return { total, pair };
}

function strongPairs(total: Map<string, number>, pair: Map<string, number>) {
  const out: { strength: number; a: string; b: string }[] = [];
  for (const [k, both] of pair) {
    if (both < MIN_SUPPORT) continue;
    const [a, b] = k.split('\0');
    const either = total.get(a)! + total.get(b)! - both;   // Жаккар: разом / бодай раз
    const strength = both / either;
    if (strength >= MIN_STRENGTH) out.push({ strength, a, b });
  }
  return out.sort((x, y) =>
    y.strength - x.strength || x.a.localeCompare(y.a) || x.b.localeCompare(y.b));
}

/** зливаємо сильні пари в осі — класичний union-find */
function cluster(pairs: { a: string; b: string }[], files: Iterable<string>) {
  const parent = new Map<string, string>();
  const find = (x: string): string => {
    if (!parent.has(x)) parent.set(x, x);
    if (parent.get(x) !== x) parent.set(x, find(parent.get(x)!));
    return parent.get(x)!;
  };
  for (const { a, b } of pairs) parent.set(find(a), find(b));

  const groups = new Map<string, string[]>();
  for (const f of files) {
    const root = find(f);
    if (!groups.has(root)) groups.set(root, []);
    groups.get(root)!.push(f);
  }
  return [...groups.values()].filter(g => g.length > 1).sort((a, b) => b.length - a.length);
}

const { total, pair } = coChange(history());
const pairs = strongPairs(total, pair);

console.log(`пари, що міняються разом (сила ≥ ${MIN_STRENGTH}):`);
for (const { strength, a, b } of pairs)
  console.log(`  ${strength.toFixed(2)}  ${a}  ↔  ${b}`);

console.log('\nосі зміни:');
for (const [i, axis] of cluster(pairs, total.keys()).entries()) {
  console.log(`  вісь #${i + 1} — файлів: ${axis.length}`);
  for (const f of axis.sort()) console.log(`      ${f.padEnd(36)} змін: ${total.get(f)}`);
}
