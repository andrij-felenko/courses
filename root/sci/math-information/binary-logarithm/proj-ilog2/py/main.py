M64 = (1 << 64) - 1

def de_bruijn_b2_6() -> int:
    """Найменша лексикографічно послідовність B(2,6), укладена в 64 біти."""
    a, seq = [0] * 12, []

    def gen(t, p):                       # алгоритм Фредриксена — Кесслера — Майорани
        if t > 6:
            if 6 % p == 0:
                seq.extend(a[1:p + 1])
            return
        a[t] = a[t - p]
        gen(t + 1, p)
        for j in range(a[t - p] + 1, 2):
            a[t] = j
            gen(t + 1, t)

    gen(1, 1)
    c = 0
    for bit in seq:                      # seq[0] стає найстаршим бітом
        c = (c << 1) | bit
    return c

C = de_bruijn_b2_6()
assert C.bit_length() == 58, 'угорі мусить бути шість нулів'
print('стала:  0x%016x' % C)             # 0x0218a392cd3d5dbf

tab = [None] * 64
for k in range(64):
    idx = (((1 << k) * C) & M64) >> 58
    assert tab[idx] is None, 'колізія — стала непридатна'
    tab[idx] = k
print('таблиця:', tab)
