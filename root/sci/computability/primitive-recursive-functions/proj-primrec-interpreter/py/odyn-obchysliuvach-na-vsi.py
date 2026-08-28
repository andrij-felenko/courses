def ev(e, xs):
    match e:
        case Zero():       return 0
        case Succ():       return xs[0] + 1
        case Proj(i):      return xs[i - 1]
        case Comp(f, gs):  return ev(f, [ev(g, xs) for g in gs])
        case Rec(base, step):
            *pre, y = xs                   # x⃗ і лічильник y
            if y == 0:
                return ev(base, pre)       # база: значення на нулі
            prev = ev(e, pre + [y - 1])    # спускаємося на сходинку нижче
            return ev(step, pre + [y - 1, prev])
