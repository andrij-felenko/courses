// чи існує шлях frm ~> to через наявні ребра (транзитивна досяжність)?
function reaches(edges, frm, to) {
  const adj = new Map();
  for (const [a, b] of edges) (adj.get(a) ?? adj.set(a, []).get(a)).push(b);
  const seen = new Set([frm]);
  const queue = [frm];
  while (queue.length) {
    const x = queue.shift();
    for (const y of adj.get(x) ?? []) {
      if (y === to) return true;              // дістались забороненої цілі
      if (!seen.has(y)) { seen.add(y); queue.push(y); }
    }
  }
  return false;
}
// граф A->B->C: reaches(edges,"A","C") === true, хоч прямого ребра A->C нема
