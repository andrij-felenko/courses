def main() -> int:
    branches = [
        Branch(2, 0),   # 0: V  — C–A
        Branch(0, 2),   # 1: R3 — A–C
        Branch(0, 1),   # 2: R1 — A–B
        Branch(1, 2),   # 3: R2 — B–C
    ]
    name = ["V", "R3", "R1", "R2"]
    N, B = 3, 4

    g = Graph(N)
    for i, br in enumerate(branches):
        g.add_edge(i, br.a, br.b)

    seen = g.dfs(0)                 # старт із вузла A = 0

    # seen         == 3  → граф зв'язний (охопив усі 3 вузли)
    # g.n_tree     == N - 1     == 2 гілки в кістяковому дереві
    # len(g.chord) == B - N + 1 == 2 хорди, кожна замикає свій контур
    # g.chord[0:2] → самі хорди (тут — R3 і R2)
    if seen != N or g.n_tree != N - 1 or len(g.chord) != B - N + 1:
        return 1                            # топологія не збіглася

    # кожна хорда → свій фундаментальний контур
    for c in g.chord:
        loop = g.collect_loop(c, branches)
        print(f"контур хорди {name[c]}:", " ".join(name[b] for b in loop))
    return 0
