function checkLayers(g: Graph, level: Map<string, number>): string[] {
  // level: модуль → номер шару (більший = вищий). Ребро вгору — порушення.
  const bad: string[] = [];
  const lv = (m: string) => level.get(m) ?? 0;
  for (const [u, deps] of g)
    for (const v of deps)
      if (lv(u) < lv(v))                               // залежність веде ВГОРУ
        bad.push(`${u}(р.${lv(u)}) → ${v}(р.${lv(v)}): ребро вгору`);
  return bad;
}
