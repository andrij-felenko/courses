enum Color { White, Gray, Black }

function findCycles(g: Graph): string[][] {
  const color = new Map<string, Color>([...g.keys()].map(v => [v, Color.White]));
  const stack: string[] = [];                    // поточний ланцюжок занурення (сірі вершини)
  const cycles: string[][] = [];

  const dfs = (v: string): void => {
    color.set(v, Color.Gray);                    // входимо — вершина тепер у ланцюжку
    stack.push(v);
    for (const w of g.get(v) ?? []) {
      const c = color.get(w) ?? Color.White;
      if (c === Color.Gray) {                    // ребро в СІРУ → зворотне ребро → цикл
        cycles.push(stack.slice(stack.indexOf(w)));   // хвіст стеку від w до v — саме коло
      } else if (c === Color.White) {
        dfs(w);                                  // ще не ходили — крок углиб
      }
      // Black — гілка вже вийдена, пропускаємо
    }
    color.set(v, Color.Black);                   // виходимо — вершина й нащадки позаду
    stack.pop();
  };

  for (const v of g.keys())
    if (color.get(v) === Color.White) dfs(v);    // ліс: запуск із кожної ще білої вершини
  return cycles;
}
