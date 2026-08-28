N, K = 32, 24
NSYM = N - K                      # 8 контрольних байтів
T = NSYM // 2                     # t = 4: стільки байтових помилок ловимо

def p_mul(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        if a:
            for j, b in enumerate(q):
                if b:
                    r[i + j] ^= mul(a, b)
    return r

def p_eval(p, x):                 # Горнер; старший степінь — перший
    y = 0
    for c in p:
        y = mul(y, x) ^ c
    return y

def rs_generator(nsym):
    g = [1]
    for i in range(nsym):
        g = p_mul(g, [1, pw(2, i)])   # g(x) = ∏ (x − αⁱ), i = 0…nsym−1
    return g

def rs_encode(msg, nsym):
    """Систематичне: дані лишаються як є, контрольні байти — остача."""
    g = rs_generator(nsym)
    buf = list(msg) + [0] * nsym
    for i in range(len(msg)):
        coef = buf[i]
        if coef:
            for j in range(1, len(g)):
                buf[i + j] ^= mul(g[j], coef)
    return list(msg) + buf[len(msg):]
