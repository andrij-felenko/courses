import { readdirSync, statSync, readFileSync } from "node:fs";
import { join, relative, sep } from "node:path";

type Graph = Map<string, Set<string>>;   // модуль → модулі, від яких він залежить

// import ... from "spec"  /  export ... from "spec"
const IMPORT_RE = /(?:import|export)[^'"]*?from\s*['"]([^'"]+)['"]/g;

const moduleOf = (root: string, file: string) => relative(root, file).split(sep)[0];

function walk(dir: string): string[] {
  const out: string[] = [];
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else if (/\.tsx?$/.test(name)) out.push(full);
  }
  return out;
}

function buildGraph(root: string): Graph {
  const files = walk(root);
  const layers = new Set(files.map(f => moduleOf(root, f)));      // усі реальні модулі-теки
  const g: Graph = new Map([...layers].map(l => [l, new Set()]));

  for (const file of files) {
    const from = moduleOf(root, file);
    for (const m of readFileSync(file, "utf8").matchAll(IMPORT_RE)) {
      const to = m[1].split("/")[0];                             // перший сегмент специфікатора
      if (layers.has(to) && to !== from) g.get(from)!.add(to);   // лише внутрішні міжмодульні ребра
    }
  }
  return g;
}
