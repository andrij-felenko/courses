PREC = {"+": 1, "-": 1, "*": 2, "/": 2}

def to_rpn(tokens):
    """Інфікс → постфікс. Один прохід = одна дія."""
    out, ops, i = [], [], 0
    while i < len(tokens) or ops:
        v = (len(tokens) - i, len(ops))          # варіант — ПАРА
        t = tokens[i] if i < len(tokens) else None

        if t is not None and t not in PREC and t not in ("(", ")"):
            out.append(t); i += 1                            # число — одразу у вихід
        elif t == "(":
            ops.append(t); i += 1
        elif t == ")" and ops and ops[-1] == "(":
            ops.pop(); i += 1                                # дужка закрилася
        elif t is not None and t in PREC and (
                not ops or ops[-1] == "(" or PREC[ops[-1]] < PREC[t]):
            ops.append(t); i += 1                            # оператор іде вгору
        else:
            out.append(ops.pop())                            # старший оператор — у вихід

        assert (len(tokens) - i, len(ops)) < v    # кортежі порівнюються словниково
    return out
