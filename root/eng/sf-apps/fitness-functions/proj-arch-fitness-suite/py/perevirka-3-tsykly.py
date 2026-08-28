WHITE, GRAY, BLACK = 0, 1, 2

def find_cycle(g: dict[str, set[str]]) -> list[str] | None:
    color = {u: WHITE for u in g}
    parent: dict[str, str] = {}

    def walk(u: str) -> list[str] | None:
        color[u] = GRAY                       # u зайшов у стек обходу
        for v in sorted(g[u]):                # sorted — щоб звіт був детермінований
            if color[v] == GRAY:              # ребро у СІРЕ = замкнення назад
                path = [u]
                while path[-1] != v:          # підіймаємось по батьках u → … → v
                    path.append(parent[path[-1]])
                path.reverse()                # тепер v → … → u
                path.append(v)                # ребро u → v замикає цикл
                return path
            if color[v] == WHITE:
                parent[v] = u
                found = walk(v)
                if found:
                    return found
        color[u] = BLACK                      # u й усе під ним оброблено
        return None

    for u in g:
        if color[u] == WHITE:
            found = walk(u)
            if found:
                return found                  # напр. ['orders', 'report', 'orders']
    return None
