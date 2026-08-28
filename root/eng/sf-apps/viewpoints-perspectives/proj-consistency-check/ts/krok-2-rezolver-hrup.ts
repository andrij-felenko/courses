// Групуємо прояви у зв'язні компоненти графа відповідностей.
// Кожна група — усі прояви ОДНОГО логічного елемента в різних в'ю.
function resolveGroups(desc: Description): Manifestation[][] {
  const byId = new Map(desc.manifestations.map(m => [m.id, m] as const));

  // ненапрямлений список суміжності
  const adj = new Map<string, string[]>();
  const touch = (x: string) => { if (!adj.has(x)) adj.set(x, []); return adj.get(x)!; };
  for (const m of desc.manifestations) touch(m.id);
  for (const { a, b } of desc.correspondences) { touch(a).push(b); touch(b).push(a); }

  const seen = new Set<string>();     // ← без цього циклічна відповідність зациклить обхід
  const groups: Manifestation[][] = [];
  for (const start of adj.keys()) {
    if (seen.has(start)) continue;
    const group: Manifestation[] = [];
    const stack = [start];
    seen.add(start);
    while (stack.length) {
      const x = stack.pop()!;
      const m = byId.get(x);
      if (m) group.push(m);
      for (const y of adj.get(x)!) if (!seen.has(y)) { seen.add(y); stack.push(y); }
    }
    groups.push(group);
  }
  return groups;
}
