import secrets   # криптографічно надійне джерело, не random!

def is_probable_prime(n, k=40):
    if n < 2:
        return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n == sp:      return True
        if n % sp == 0:  return False
    # n − 1 = 2^s · d
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2;  s += 1
    for _ in range(k):
        a = 2 + secrets.randbelow(n - 3)     # основа з [2, n−2], криптоджерело
        x = pow(a, d, n)                     # рідний великий int — переповнення немає
        if x == 1 or x == n - 1:
            continue                         # основа мовчить
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break                        # дійшли до −1 — мовчить
        else:
            return False                     # −1 не трапилось: свідок → складене
    return True                              # усі k основ промовчали
