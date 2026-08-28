from collections import deque

def csg_accepts(rules, start, w):
    """rules: список (ліва, права) з |ліва| ≤ |права|, рядки над V ∪ Σ.
    Повертає True ⟺ start ⇒* w. ЗАВЖДИ зупиняється."""
    n = len(w)
    seen, queue = {start}, deque([start])
    while queue:
        s = queue.popleft()
        if s == w:
            return True
        for lhs, rhs in rules:
            i = s.find(lhs)
            while i != -1:
                t = s[:i] + rhs + s[i + len(lhs):]
                # правила не вкорочують → форми довші за w — глухий кут
                if len(t) <= n and t not in seen:
                    seen.add(t)
                    queue.append(t)
                i = s.find(lhs, i + 1)
    return False
