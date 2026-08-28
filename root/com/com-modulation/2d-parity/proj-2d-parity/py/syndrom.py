def syndromes(w):
    """srow[r] — XOR усього рядка r, scol[c] — XOR усього стовпця c.
    Нуль — перевірка ціла, одиниця — зламана."""
    R1, C1 = len(w), len(w[0])
    srow = [0] * R1
    scol = [0] * C1
    for r in range(R1):
        for c in range(C1):
            b = w[r][c]
            srow[r] ^= b
            scol[c] ^= b
    return srow, scol
