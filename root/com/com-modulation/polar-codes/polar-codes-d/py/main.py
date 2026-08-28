def polar_encode(u):
    """u — вектор із N = 2**n бітів (дані на вільних позиціях, 0 на заморожених).
    Повертає кодове слово x. Перетворення — рекурсивне змішування половин."""
    n = len(u)
    if n == 1:
        return u[:]
    half = n // 2
    a = polar_encode(u[:half])          # верхня половина
    b = polar_encode(u[half:])          # нижня половина
    return [a[i] ^ b[i] for i in range(half)] + b   # x = (a⊕b, b)
