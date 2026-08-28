# arch/cycles.py — знайти цикл (обхід у глибину, три кольори); повернути сам ланцюг для звіту
def find_cycle(graph):
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {n: WHITE for n in graph}
    stack = []
    def visit(n):
        colour[n] = GREY; stack.append(n)           # сірий = на поточному стеку рекурсії
        for m in graph.get(n, ()):
            if colour.get(m, WHITE) == GREY:         # ребро в сірого = ребро назад = ЦИКЛ
                return stack[stack.index(m):] + [m]  # замкнений ланцюг для повідомлення
            if colour.get(m, WHITE) == WHITE:
                found = visit(m)
                if found: return found
        stack.pop(); colour[n] = BLACK               # відходимо — вузол пройдено повністю
        return None
    for n in graph:
        if colour[n] == WHITE:
            found = visit(n)
            if found: return found
    return None
