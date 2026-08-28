def solve_gf2(A, b):
    """Розв'язати A·x = b над GF(2). Повертає x або None, якщо розв'язок не єдиний."""
    A = [row[:] for row in A]
    b = b[:]
    m = len(A)
    n = len(A[0]) if m else 0
    where = [-1] * n                 # рядок-опора для кожного стовпця
    row = 0
    for col in range(n):
        piv = next((r for r in range(row, m) if A[r][col]), None)
        if piv is None:              # у цьому стовпці немає опори → вільна змінна
            continue
        A[row], A[piv] = A[piv], A[row]
        b[row], b[piv] = b[piv], b[row]
        where[col] = row
        for r in range(m):           # обнулити стовпець в усіх інших рядках
            if r != row and A[r][col]:
                A[r] = [a ^ p for a, p in zip(A[r], A[row])]
                b[r] ^= b[row]
        row += 1
    if any(w == -1 for w in where):  # лишилася вільна змінна → розв'язок не єдиний
        return None
    for r in range(row, m):          # рядок «0 = 1» → суперечність
        if b[r]:
            return None
    x = [0] * n
    for col in range(n):
        x[col] = b[where[col]]
    return x
