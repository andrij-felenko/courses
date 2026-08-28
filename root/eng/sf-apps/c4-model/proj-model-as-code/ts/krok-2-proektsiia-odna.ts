const el = (m: Model, id: string) => m.elements.find(e => e.id === id)!;
const parentOf = (m: Model, id: string) => el(m, id).parent;

function isDescendant(m: Model, id: string, of: string): boolean {
  let cur = parentOf(m, id);
  while (cur) { if (cur === of) return true; cur = parentOf(m, cur); }
  return false;
}

// представник вузла на заданому рівні — найгрубша видима коробка над ним
function representative(m: Model, id: string, scope: string, level: Level): string {
  if (level === "context")
    return id === scope || isDescendant(m, id, scope) ? scope : id;
  // container: descendant scope-у піднімаємо до контейнера (прямої дитини scope)
  if (id === scope) return scope;
  if (isDescendant(m, id, scope)) {
    let cur = id;
    while (parentOf(m, cur) !== scope) cur = parentOf(m, cur)!;
    return cur;
  }
  return id;
}

function nodeDecl(m: Model, id: string): string {
  const e = el(m, id);
  const label = e.technology ? `${e.name}<br/>[${e.technology}]` : e.name;
  return `${id}["${label}"]`;
}

function project(m: Model, scope: string, level: Level): string {
  // 1. переписуємо кожне ребро на представників і прибираємо петлі
  const edges = new Map<string, { from: string; to: string; label: string }>();
  for (const r of m.relations) {
    const a = representative(m, r.from, scope, level);
    const b = representative(m, r.to, scope, level);
    if (a === b) continue;                       // сховалось усередині коробки
    edges.set(`${a}->${b}`, { from: a, to: b, label: r.label });
  }
  // 2. видимі вузли — кінці ребер + гарантовано сам scope / його контейнери
  const visible = new Set<string>();
  for (const e of edges.values()) { visible.add(e.from); visible.add(e.to); }
  if (level === "context") visible.add(scope);
  else for (const e of m.elements) if (e.parent === scope) visible.add(e.id);

  // 3. рендер у текст Mermaid
  const ids = m.elements.filter(e => visible.has(e.id)).map(e => e.id);
  const out = ["flowchart TB"];
  if (level === "container") {
    out.push(`  subgraph ${scope}["${el(m, scope).name}"]`);
    for (const id of ids) if (parentOf(m, id) === scope) out.push(`    ${nodeDecl(m, id)}`);
    out.push("  end");
    for (const id of ids) if (parentOf(m, id) !== scope && id !== scope) out.push(`  ${nodeDecl(m, id)}`);
  } else {
    for (const id of ids) out.push(`  ${nodeDecl(m, id)}`);
  }
  for (const e of edges.values()) out.push(`  ${e.from} -->|"${e.label}"| ${e.to}`);
  return out.join("\n");
}

console.log(project(shop, "shop", "context"));
console.log(project(shop, "shop", "container"));
