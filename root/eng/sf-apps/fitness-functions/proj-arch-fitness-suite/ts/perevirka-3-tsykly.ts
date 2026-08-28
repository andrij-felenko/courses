const WHITE = 0, GRAY = 1, BLACK = 2;

function findCycle(g: Graph): string[] | null {
  const color = new Map<string, number>([...g.keys()].map(u => [u, WHITE] as [string, number]));
  const parent = new Map<string, string>();

  function walk(u: string): string[] | null {
    color.set(u, GRAY);                              // u зайшов у стек обходу
    for (const v of [...g.get(u)!].sort()) {         // sort — щоб звіт був детермінований
      if (color.get(v) === GRAY) {                   // ребро у СІРЕ = замкнення назад
        const path = [u];
        while (path[path.length - 1] !== v)          // підіймаємось по батьках u → … → v
          path.push(parent.get(path[path.length - 1])!);
        path.reverse();                              // тепер v → … → u
        path.push(v);                                // ребро u → v замикає цикл
        return path;
      }
      if (color.get(v) === WHITE) {
        parent.set(v, u);
        const found = walk(v);
        if (found) return found;
      }
    }
    color.set(u, BLACK);                             // u й усе під ним оброблено
    return null;
  }

  for (const u of g.keys())
    if (color.get(u) === WHITE) {
      const found = walk(u);
      if (found) return found;                       // напр. ['orders','report','orders']
    }
  return null;
}
