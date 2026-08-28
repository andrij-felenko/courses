class NodeMap:
    def __init__(self):
        self.id: dict[Point, int] = {}       # точка → вузол
        self.pt: list[Point] = []            # вузол → координата (для діагностики)

    def node_at(self, p: Point) -> int:
        n = self.id.get(p)
        if n is not None:                    # уже є вузол на цій точці
            return n
        n = len(self.pt)
        self.id[p] = n
        self.pt.append(p)
        return n                             # новий вузол на новій точці


# Будуємо геометричні ланцюги: спільна координата → спільний вузол;
# кінці кожного дроту зливаємо; Т-дотики ловимо окремим проходом.
def build_geometry(wires: list[Wire], pins: list[Pin], nm: NodeMap) -> DSU:
    # 1) Заводимо вузли на всіх кінцях дротів і всіх пінах (збіг точок = той самий вузол).
    for w in wires:
        nm.node_at(w.a)
        nm.node_at(w.b)
    for p in pins:
        nm.node_at(p.at)

    dsu = DSU(len(nm.pt))

    # 2) Кінці того самого дроту — очевидно один ланцюг.
    for w in wires:
        dsu.unite(nm.node_at(w.a), nm.node_at(w.b))

    # 3) Т-ДОТИКИ: вузол (пін чи кінець дроту), що лежить УСЕРЕДИНІ іншого дроту.
    #    Без цього кроку трійник «кінець у середину» загубився б.
    for v, p in enumerate(nm.pt):
        for w in wires:
            if p == w.a or p == w.b:         # кінці вже злиті в кроці 2
                continue
            if point_on_wire(p, w):          # p сидить на тілі дроту w
                dsu.unite(v, nm.node_at(w.a))  # приєднати до того дроту
    return dsu
