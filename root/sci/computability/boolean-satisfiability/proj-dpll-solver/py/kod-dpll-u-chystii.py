def simplify(clauses, lit):
    """Призначити lit=істина: викинути вдоволені клаузи, вирізати -lit із решти."""
    out = []
    for cl in clauses:
        if lit in cl:
            continue                              # клауза вже істинна — геть
        if -lit in cl:
            out.append([x for x in cl if x != -lit])   # -lit хибний — вирізаємо
        else:
            out.append(cl)
    return out

def find_unit(clauses):
    """Перша одинична клауза (єдиний уцілілий літерал), або None."""
    for cl in clauses:
        if len(cl) == 1:
            return cl[0]
    return None

def find_pure(clauses):
    """Чистий літерал: змінна лише в одній полярності. Найменша за номером — детермінізм."""
    pos, neg = set(), set()
    for cl in clauses:
        for lit in cl:
            (pos if lit > 0 else neg).add(abs(lit))
    for v in sorted(pos | neg):
        if v not in neg:  return v                # трапляється лише як +v
        if v not in pos:  return -v               # трапляється лише як −v
    return None

def dpll(clauses, model):
    """Свідок (dict змінна→bool) або None, якщо формула нездійсненна."""
    if any(len(cl) == 0 for cl in clauses):
        return None                               # порожня клауза — суперечність
    if not clauses:
        return model                              # клауз не лишилось — усе вдоволено

    u = find_unit(clauses)                         # 1. поширення одиничних клауз
    if u is not None:
        return dpll(simplify(clauses, u), {**model, abs(u): u > 0})

    p = find_pure(clauses)                         # 2. вилучення чистих літералів
    if p is not None:
        return dpll(simplify(clauses, p), {**model, abs(p): p > 0})

    lit = clauses[0][0]                            # 3. вгадування + повернення
    for guess in (lit, -lit):
        r = dpll(simplify(clauses, guess), {**model, abs(guess): guess > 0})
        if r is not None:
            return r
    return None

if __name__ == "__main__":
    # (x₁ ∨ ¬x₂) ∧ (x₂ ∨ x₃) ∧ (¬x₁ ∨ ¬x₃)
    formula = [[1, -2], [2, 3], [-1, -3]]
    model = dpll(formula, {})
    print("UNSAT" if model is None else f"SAT: {model}")
    # → SAT: {1: True, 3: False, 2: True}   тобто x₁=1, x₂=1, x₃=0
