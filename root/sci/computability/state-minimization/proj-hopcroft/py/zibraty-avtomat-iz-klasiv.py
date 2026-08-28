def rebuild(delta, accept, start, blocks):
    """Зібрати мінімальний автомат: по одному стану на клас."""
    where = {s: i for i, b in enumerate(blocks) for s in b}
    new_delta, new_accept = [], set()
    for i, b in enumerate(blocks):
        rep = min(b)                           # будь-який представник класу
        new_delta.append([where[t] for t in delta[rep]])
        if rep in accept:
            new_accept.add(i)
    return new_delta, new_accept, where[start]


def minimize(delta, accept, start):
    delta, accept, start = prune(delta, accept, start)
    return rebuild(delta, accept, start, hopcroft(delta, accept))
