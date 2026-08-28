def factor(n: int):
    d = 2
    while d * d <= n:                  # досить дійти до √n
        if n % d == 0:
            return d, n // d
        d += 1
    return None

def break_key(pub):
    """Маючи лише відкритий ключ — дістати таємний."""
    n, e = pub
    p, q = factor(n)
    return n, inverse(e, (p - 1) * (q - 1))

assert break_key((55, 3)) == (55, 27)  # d здобуто з самого лише (n, e)
