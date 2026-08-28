def ev_memo(e, xs, cache):
    key = (id(e), tuple(xs))
    if key in cache:
        return cache[key]                         # уже рахували — віддаємо готове
    match e:
        case Zero():      r = 0
        case Succ():      r = xs[0] + 1
        case Proj(i):     r = xs[i - 1]
        case Comp(f, gs): r = ev_memo(f, [ev_memo(g, xs, cache) for g in gs], cache)
        case Rec(base, step):
            *pre, y = xs
            if y == 0:
                r = ev_memo(base, pre, cache)
            else:
                prev = ev_memo(e, pre + [y - 1], cache)
                r = ev_memo(step, pre + [y - 1, prev], cache)
    cache[key] = r
    return r
