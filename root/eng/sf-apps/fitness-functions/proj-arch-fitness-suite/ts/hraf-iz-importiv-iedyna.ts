// граф: модуль → модулі, від яких він ПРЯМО залежить
type Graph = Map<string, Set<string>>;

function buildGraph(edges: [string, string][]): Graph {
  const g: Graph = new Map();
  const node = (m: string) => g.get(m) ?? g.set(m, new Set()).get(m)!;
  for (const [src, dst] of edges) {
    node(src); node(dst);                 // вузол існує навіть без вихідних ребер
    if (src !== dst) node(src).add(dst);  // самопосилання модуля на себе — не ребро
  }
  return g;
}
