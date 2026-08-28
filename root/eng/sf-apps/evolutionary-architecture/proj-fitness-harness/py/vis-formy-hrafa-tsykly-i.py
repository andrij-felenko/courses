WHITE, GRAY, BLACK = 0, 1, 2

def find_cycles(g: dict[str, set[str]]) -> list[list[str]]:
    color = {v: WHITE for v in g}
    stack: list[str] = []                        # поточний ланцюжок занурення (сірі вершини)
    cycles: list[list[str]] = []

    def dfs(v: str) -> None:
        color[v] = GRAY                          # входимо — вершина тепер у ланцюжку
        stack.append(v)
        for w in g.get(v, ()):
            if color.get(w, WHITE) == GRAY:      # ребро в СІРУ → зворотне ребро → цикл
                cycles.append(stack[stack.index(w):])   # хвіст стеку від w до v — саме коло
            elif color.get(w, WHITE) == WHITE:
                dfs(w)                           # ще не ходили — крок углиб
            # BLACK — гілка вже вийдена, пропускаємо
        color[v] = BLACK                         # виходимо — вершина й нащадки позаду
        stack.pop()

    for v in g:
        if color[v] == WHITE:                    # ліс: запуск із кожної ще білої вершини
            dfs(v)
    return cycles
