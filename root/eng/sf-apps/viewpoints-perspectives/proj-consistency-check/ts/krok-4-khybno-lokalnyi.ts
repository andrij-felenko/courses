interface FalseLocal { from: string; to: string; why: string; }

function checkFalseLocal(desc: Description, groups: Manifestation[][]): FalseLocal[] {
  // функц. елемент → його вузли розгортання (через групу відповідностей)
  const info = new Map<string, { nodes: string[]; label: string }>();
  for (const group of groups) {
    const fe = group.find(m => m.view === 'functional');
    const dep = group.find(m => m.view === 'deployment');
    if (fe) info.set(fe.id, { nodes: dep ? (desc.deployment.hosts[dep.id] ?? []) : [], label: fe.label });
  }

  // мережеві зв'язки в обидва боки — для O(1) перевірки «чи є мережа»
  const linked = new Set<string>();
  for (const [x, y] of desc.deployment.links) { linked.add(`${x}|${y}`); linked.add(`${y}|${x}`); }
  const crosses = (a: string[], b: string[]) =>
    a.some(na => b.some(nb => na !== nb && linked.has(`${na}|${nb}`)));

  const bad: FalseLocal[] = [];
  for (const call of desc.calls) {
    if (call.kind !== 'local') continue;                 // перевіряємо лише заявлені local
    const from = info.get(call.from), to = info.get(call.to);
    if (!from || !to) continue;
    if (to.nodes.length > 1)
      bad.push({ from: from.label, to: to.label,
                 why: `ціль реплікована на ${to.nodes.length} вузли — виклик іде через балансувальник (мережа)` });
    else if (crosses(from.nodes, to.nodes))
      bad.push({ from: from.label, to: to.label, why: "кінці на різних вузлах, з'єднаних мережею" });
  }
  return bad;
}
