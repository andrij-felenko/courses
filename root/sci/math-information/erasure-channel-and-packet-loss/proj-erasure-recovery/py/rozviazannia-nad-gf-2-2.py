def recover(H, received):
    """Відновити стерті (None) символи лінійного коду з перевірною матрицею H."""
    erased = [j for j, v in enumerate(received) if v is None]
    known  = [j for j, v in enumerate(received) if v is not None]
    A = [[H[r][j] for j in erased] for r in range(len(H))]                 # Hₑ
    s = [sum(H[r][j] * received[j] for j in known) % 2 for r in range(len(H))]
    x = solve_gf2(A, s)
    if x is None:
        return None                  # стерто більше, ніж код здатен витягти
    out = list(received)
    for idx, j in enumerate(erased):
        out[j] = x[idx]
    return out
