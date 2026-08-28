def compile(e):
    match e:
        case Zero():      return lambda xs: 0
        case Succ():      return lambda xs: xs[0] + 1
        case Proj(i):     return lambda xs, i=i: xs[i - 1]
        case Comp(f, gs):
            cf, cg = compile(f), [compile(g) for g in gs]
            return lambda xs: cf([c(xs) for c in cg])
        case Rec(base, step):
            cb, cs = compile(base), compile(step)
            def run(xs):
                *pre, y = xs
                acc = cb(pre)
                for k in range(y):                 # межа y відома до входу в цикл
                    acc = cs(pre + [k, acc])
                return acc
            return run
