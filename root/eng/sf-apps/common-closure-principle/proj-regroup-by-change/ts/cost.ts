// tools/cost.ts — ціна зміни: граф компонентів + замикання перезбирання
import { readdirSync, readFileSync, existsSync, statSync } from 'node:fs';
import { join, resolve, dirname, relative } from 'node:path';

const SRC = resolve('src');
const IMPORT_RE = /\bfrom\s*['"]([^'"]+)['"]|\brequire\(\s*['"]([^'"]+)['"]\s*\)/g;

/** компонент файла = перший сегмент шляху під src/ */
const componentOf = (file: string): string =>
  relative(SRC, resolve(file)).split(/[\\/]/)[0];

function sources(dir = SRC, acc: string[] = []): string[] {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) sources(p, acc);
    else if (/\.tsx?$/.test(name) && !name.endsWith('.d.ts')) acc.push(p);
  }
  return acc;
}

/** './x' → абсолютний шлях файла; зовнішній пакет → null (поза нашим графом) */
function resolveSpec(from: string, spec: string): string | null {
  if (!spec.startsWith('.')) return null;
  const base = resolve(dirname(from), spec);
  for (const c of [base, `${base}.ts`, `${base}.tsx`, join(base, 'index.ts')])
    if (existsSync(c) && statSync(c).isFile()) return c;
  return null;
}

/** size: компонент → скільки файлів; deps: компонент → на кого спирається */
function scan() {
  const size = new Map<string, number>();
  const deps = new Map<string, Set<string>>();

  for (const file of sources()) {
    const here = componentOf(file);
    size.set(here, (size.get(here) ?? 0) + 1);
    if (!deps.has(here)) deps.set(here, new Set());

    for (const m of readFileSync(file, 'utf8').matchAll(IMPORT_RE)) {
      const target = resolveSpec(file, m[1] ?? m[2]);
      if (!target) continue;
      const to = componentOf(target);
      if (to !== here) deps.get(here)!.add(to);   // ребро лише МІЖ компонентами
    }
  }
  return { size, deps };
}

/** зворотні ребра: хто чекає перезбирання, коли міняється X */
function reverse(deps: Map<string, Set<string>>) {
  const rev = new Map<string, Set<string>>();
  for (const c of deps.keys()) rev.set(c, new Set());
  for (const [from, tos] of deps)
    for (const to of tos) rev.get(to)!.add(from);
  return rev;
}

/** транзитивне замикання вгору — саме це перезбере конвеєр */
function rebuildSet(rev: Map<string, Set<string>>, touched: Iterable<string>) {
  const out = new Set(touched);
  const stack = [...out];
  while (stack.length) {
    for (const up of rev.get(stack.pop()!) ?? [])
      if (!out.has(up)) { out.add(up); stack.push(up); }
  }
  return out;
}

export function cost(changed: string[]) {
  const { size, deps } = scan();
  const touched = new Set(changed.map(componentOf));
  const rebuilt = rebuildSet(reverse(deps), touched);
  const total = [...size.values()].reduce((a, b) => a + b, 0);
  const hit = [...rebuilt].reduce((a, c) => a + (size.get(c) ?? 0), 0);
  return { touched, rebuilt, components: size.size, hit, total };
}

const r = cost(process.argv.slice(2));
const list = (s: Set<string>) => [...s].sort().join(', ');
console.log(`торкнулися компонентів : ${r.touched.size}  (${list(r.touched)})`);
console.log(`перезбирається         : ${r.rebuilt.size} з ${r.components}  (${list(r.rebuilt)})`);
console.log(`файлів у перезбиранні  : ${r.hit} з ${r.total} = ${Math.round((r.hit / r.total) * 100)}%`);
