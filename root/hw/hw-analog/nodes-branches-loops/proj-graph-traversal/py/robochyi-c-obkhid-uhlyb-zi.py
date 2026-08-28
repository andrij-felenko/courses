from dataclasses import dataclass, field


@dataclass
class Branch:
    """Гілка з'єднує вузли a та b (номер гілки = індекс у списку)."""
    a: int
    b: int


@dataclass
class Graph:
    n: int
    # список суміжності: для вузла v — пари (сусід, номер гілки)
    adj: list[list[tuple[int, int]]] = field(init=False)
    visited: list[bool] = field(init=False)      # вузол уже відкрито?
    br_done: set[int] = field(default_factory=set)   # гілку вже класифіковано?
    parent_node: list[int] = field(init=False)   # батьківський вузол (-1 = корінь)
    parent_br: list[int] = field(init=False)     # гілка до батька
    chord: list[int] = field(default_factory=list)   # список хорд
    n_tree: int = 0

    def __post_init__(self):
        self.adj = [[] for _ in range(self.n)]
        self.visited = [False] * self.n
        self.parent_node = [-1] * self.n
        self.parent_br = [0] * self.n

    def add_edge(self, br: int, a: int, b: int) -> None:
        self.adj[a].append((b, br))
        self.adj[b].append((a, br))              # граф неорієнтований

    def dfs(self, start: int) -> int:
        """Обхід углиб від start; повертає, скільки вузлів охоплено."""
        stack = [start]
        self.visited[start] = True               # вузол відкриваємо при ВХОДІ
        self.parent_node[start] = -1
        seen = 1

        while stack:
            v = stack.pop()                      # беремо з вершини стека
            for u, br in self.adj[v]:
                if br in self.br_done:           # кожну гілку класифікуємо РАЗ
                    continue
                self.br_done.add(br)
                if not self.visited[u]:          # веде в новий вузол → гілка дерева
                    self.visited[u] = True
                    seen += 1
                    self.parent_node[u] = v
                    self.parent_br[u] = br
                    self.n_tree += 1
                    stack.append(u)              # у стек кладемо лише НОВІ вузли
                else:                            # веде в уже відкритий вузол → хорда
                    self.chord.append(br)
        return seen
