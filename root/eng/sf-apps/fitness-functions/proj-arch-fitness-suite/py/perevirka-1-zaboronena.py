def reaches(g: dict[str, set[str]], src: str, dst: str) -> bool:
    """Чи є напрямлений шлях src → … → dst."""
    seen, stack = {src}, [src]
    while stack:
        u = stack.pop()
        for v in g.get(u, ()):        # порядок обходу не важить — шукаємо сам факт шляху
            if v == dst:
                return True
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return False

def check_forbidden(g, rules: list[tuple[str, str]]) -> list[str]:
    """rules: пари (X, Y) зі змістом «X не сміє досягати Y»."""
    return [f"{x} ⇏ {y}: є шлях {x} → … → {y}"
            for x, y in rules if reaches(g, x, y)]
