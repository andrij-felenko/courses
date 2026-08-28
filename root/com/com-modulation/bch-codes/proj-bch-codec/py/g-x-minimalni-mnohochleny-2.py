def build_generator(t):
    taken, g = set(), [1]
    for j in range(1, 2 * t + 1):
        if j in taken:
            continue
        m = minimal_poly(j, taken)
        prod = [0] * (len(g) + len(m) - 1)   # g *= m над GF(2)
        for i, a in enumerate(g):
            if a:
                for k, b in enumerate(m):
                    prod[i + k] ^= b
        g = prod
    return g

T = 2
G = build_generator(T)                   # [1,0,0,0,1,0,1,1,1] = x⁸+x⁷+x⁶+x⁴+1
DEG = len(G) - 1                          # 8
K = N - DEG                              # 7
GINT = sum((c << i) for i, c in enumerate(G))   # 0b111010001
