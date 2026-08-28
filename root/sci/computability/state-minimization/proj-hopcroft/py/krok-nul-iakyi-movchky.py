def reachable(delta, start):
    """Стани, у які веде хоч який шлях зі start."""
    seen, stack = {start}, [start]
    while stack:
        for t in delta[stack.pop()]:
            if t not in seen:
                seen.add(t)
                stack.append(t)
    return seen


def prune(delta, accept, start):
    """Викинути недосяжне й перенумерувати стани у 0…m−1."""
    keep = sorted(reachable(delta, start))
    idx = {s: i for i, s in enumerate(keep)}
    new_delta = [[idx[t] for t in delta[s]] for s in keep]
    return new_delta, {idx[s] for s in accept if s in idx}, idx[start]
