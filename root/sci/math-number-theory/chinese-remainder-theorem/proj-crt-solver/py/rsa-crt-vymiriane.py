def sign_plain(m):
    return pow(m, d, n)                    # один степінь за 2048-бітовим модулем

def sign_crt(m):
    m1 = pow(m, dP, p)                     # два степені за 1024-бітовими модулями
    m2 = pow(m, dQ, q)
    h = (m1 - m2) * qInv % p               # Гарнер на двох модулях
    return m2 + q * h

assert sign_plain(msg) == sign_crt(msg)    # те саме число, іншим шляхом
