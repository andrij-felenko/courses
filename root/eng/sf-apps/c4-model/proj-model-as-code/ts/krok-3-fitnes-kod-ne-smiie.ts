import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";

// тека верхнього рівня → id контейнера в моделі
const SRC_ROOTS: Record<string, string> = { web: "web", api: "api", db: "db", queue: "queue" };

// дозволені ребра код→код беремо З МОДЕЛІ, а не дублюємо руками
function allowedEdges(m: Model): Set<string> {
  const code = new Set(Object.values(SRC_ROOTS));
  const allow = new Set<string>();
  for (const r of m.relations)
    if (code.has(r.from) && code.has(r.to)) allow.add(`${r.from}->${r.to}`);
  return allow;
}

function* walk(dir: string): Generator<string> {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) yield* walk(p);
    else if (p.endsWith(".ts")) yield p;
  }
}

const containerOf = (rel: string) => SRC_ROOTS[rel.split(sep)[0]];
const IMPORT = /\bfrom\s+["'](?:\.\.\/|\.\/)*([a-z]+)\//g;  // спрощено, але робить діло

// фактичні ребра «контейнер → контейнер», знайдені в коді
function actualEdges(root: string): Set<string> {
  const edges = new Set<string>();
  for (const file of walk(root)) {
    const here = containerOf(relative(root, file));
    if (!here) continue;
    const src = readFileSync(file, "utf8");
    for (const m of src.matchAll(IMPORT)) {
      const target = SRC_ROOTS[m[1]];
      if (target && target !== here) edges.add(`${here}->${target}`);
    }
  }
  return edges;
}

export function checkFitness(model: Model, root: string): void {
  const allow = allowedEdges(model);
  const bad = [...actualEdges(root)].filter(e => !allow.has(e));
  if (bad.length) {
    const lines = bad.map(e => {
      const [a, b] = e.split("->");
      return `  ✗ ${a} → ${b}: на діаграмі такої стрілки нема`;
    });
    throw new Error("C4-фітнес провалено:\n" + lines.join("\n"));
  }
  console.log("C4-фітнес: код тримається моделі ✓");
}
