def bisect(f, a, b, tol=1e-13, itmax=200):
    fa = f(a)
    for _ in range(itmax):
        m = 0.5*(a + b)
        fm = f(m)
        if fm == 0.0 or 0.5*(b - a) < tol:
            return m
        if fa*fm < 0.0:      # зміна знака ліворуч від m
            b = m
        else:                # зміна знака праворуч
            a, fa = m, fm
    return 0.5*(a + b)

def equilibria(a, b, n=2000):
    xs = [a + (b - a)*i/n for i in range(n + 1)]
    roots = []
    for i in range(n):
        f0, f1 = dU(xs[i]), dU(xs[i+1])
        if   f0 == 0.0:      r = xs[i]
        elif f0*f1 < 0.0:    r = bisect(dU, xs[i], xs[i+1])   # знак перескочив
        else:                continue
        if not roots or abs(r - roots[-1]) > 1e-6:            # без дублів
            roots.append(r)
    return roots
