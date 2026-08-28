def min_sum(checks, n, llr, max_iter=50):
    """М'який декодер. llr[i] = log(P(біт=0)/P(біт=1)) від каналу:
    знак — який біт імовірніший, модуль — наскільки впевнено."""
    owners = bit_checks_of(checks, n)
    msg = {(j, i): 0.0 for j, bits in enumerate(checks) for i in bits}
    total = list(llr)

    for it in range(max_iter):
        hard = [1 if t < 0 else 0 for t in total]
        if not any(parity(hard, bits) for bits in checks):
            return hard, it, True

        new = {}
        for j, bits in enumerate(checks):
            for i in bits:
                # думка перевірки j про біт i, спираючись ЛИШЕ на решту її бітів
                others = [llr[k] + sum(msg[(jj, k)] for jj in owners[k] if jj != j)
                          for k in bits if k != i]
                sign = 1.0
                for o in others:
                    sign *= 1.0 if o >= 0 else -1.0
                new[(j, i)] = sign * min(abs(o) for o in others)   # ланцюг рветься
        msg = new                                                  # на найслабшій ланці
        total = [llr[i] + sum(msg[(j, i)] for j in owners[i]) for i in range(n)]

    hard = [1 if t < 0 else 0 for t in total]
    return hard, max_iter, not any(parity(hard, bits) for bits in checks)
