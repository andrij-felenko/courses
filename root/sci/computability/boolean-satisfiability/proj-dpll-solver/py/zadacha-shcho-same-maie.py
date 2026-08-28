def read_dimacs(text):
    """Прочитати CNF у форматі DIMACS у список клауз (список списків int)."""
    clauses, cur = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line or line[0] in "cp":      # 'c' — коментар, 'p' — шапка
            continue
        for tok in line.split():
            n = int(tok)
            if n == 0:
                clauses.append(cur)          # нуль замикає клаузу
                cur = []
            else:
                cur.append(n)
    return clauses
