def make_interleaver(N, rng):
    perm = list(range(N))
    rng.shuffle(perm)
    inv = [0]*N
    for i, pi in enumerate(perm):
        inv[pi] = i                # inv розставляє perm назад
    return perm, inv

def turbo_encode(u, perm):
    p1 = rsc_encode(u)                        # контроль 1 — прямий порядок
    up = [u[perm[i]] for i in range(len(u))]  # ті самі біти, переставлені
    p2 = rsc_encode(up)                       # контроль 2 — на переставлених
    return u, p1, p2                          # систематичні + два контролі → 1/3
