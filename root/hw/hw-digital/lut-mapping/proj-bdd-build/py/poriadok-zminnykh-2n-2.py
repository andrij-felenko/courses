def bryant(n):
    return lambda e: any(e["x%d" % i] and e["y%d" % i] for i in range(1, n + 1))


print(" n | чергування | окремо | 2n+2 | 2^(n+1)")
for n in range(1, 9):
    inter = [v for i in range(1, n + 1) for v in ("x%d" % i, "y%d" % i)]
    separ = ["x%d" % i for i in range(1, n + 1)] + ["y%d" % i for i in range(1, n + 1)]
    a, s = BDD(inter), BDD(separ)
    print("%2d | %10d | %6d | %4d | %7d"
          % (n, a.size(a.build(bryant(n))), s.size(s.build(bryant(n))),
             2 * n + 2, 2 ** (n + 1)))
