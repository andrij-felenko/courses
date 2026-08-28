def shrink(ops, cap, kind):
    """Жадібно викидати операції, поки лишається ТА САМА розбіжність."""
    i = 0
    while i < len(ops):
        shorter = ops[:i] + ops[i + 1:]
        found = replay(shorter, cap)
        if found and found[0] == kind:
            ops = shorter          # без цієї операції теж падає — вона зайва
        else:
            i += 1
    return ops
