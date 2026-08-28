def cat_upto(A, B, n):               # (A · B), обмежена довжиною ≤ n
    Bs = upto(B, n)
    res = {u + v for u in upto(A, n) for v in Bs if len(u) + len(v) <= n}
    return sorted(res, key=KEY)

def star_upto(A, n):                 # A*, обмежена довжиною ≤ n
    pieces = [u for u in upto(A, n) if u != ""]   # ε-шматки викидаємо: інакше цикл
    reached = {""}                                # ε ∈ A* завжди
    frontier = {""}
    while frontier:                               # ширимося, доки додається нове
        nxt = set()
        for w in frontier:
            for u in pieces:
                x = w + u
                if len(x) <= n and x not in reached:
                    reached.add(x)
                    nxt.add(x)
        frontier = nxt
    return sorted(reached, key=KEY)
