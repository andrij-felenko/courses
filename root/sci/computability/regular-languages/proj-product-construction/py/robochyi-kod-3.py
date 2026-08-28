def complement(a):
    """Доповнення: поміняти приймальні й неприймальні місцями.
    Правильно ЛИШЕ на повному ДСА — тому DFA і стежить за тотальністю."""
    return DFA(a.alphabet, a.states, a.delta, a.start, a.states - a.accepting)

def witness(a):
    """Найкоротше слово, яке автомат приймає, або None, якщо мова порожня.
    Обхід завширшки СТАНАМИ (не словами!) — тому перше знайдене найкоротше."""
    parent = {a.start: None}
    queue = deque([a.start])
    while queue:
        q = queue.popleft()
        if q in a.accepting:
            out = []
            while parent[q] is not None:
                q, c = parent[q]
                out.append(c)
            return "".join(reversed(out))
        for c in sorted(a.alphabet):
            nxt = a.delta[(q, c)]
            if nxt not in parent:
                parent[nxt] = (q, c)
                queue.append(nxt)
    return None

def subset_witness(a, b):
    """None ⟺ L(a) ⊆ L(b). Інакше — найкоротше слово з L(a), якого нема в L(b)."""
    return witness(product(a, complement(b), AND))

def equiv_witness(a, b):
    """None ⟺ L(a) = L(b). Інакше — найкоротше слово, де вони розходяться."""
    return witness(product(a, b, XOR))
