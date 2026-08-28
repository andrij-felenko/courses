def to_hered(n, b):
    """Спадковий запис n за основою b: список пар (показник у такому ж записі, цифра)."""
    out, e = [], 0
    while n > 0:
        n, d = divmod(n, b)
        if d:
            out.append((to_hered(e, b), d))
        e += 1
    return out

def from_hered(h, b):
    return sum(b ** from_hered(e, b) * d for (e, d) in h)

def goodstein_step(n, b):
    return from_hered(to_hered(n, b), b + 1) - 1

n, b = 4, 2
for _ in range(6):
    print(b, n)
    n, b = goodstein_step(n, b), b + 1
# 2 4 · 3 26 · 4 41 · 5 60 · 6 83 · 7 109 · далі 139, 173, 211, 253, 299 …
