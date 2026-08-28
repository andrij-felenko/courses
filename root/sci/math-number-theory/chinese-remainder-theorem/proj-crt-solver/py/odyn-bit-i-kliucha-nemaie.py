from math import gcd

def sign_crt_faulty(m, rng):
    m1 = pow(m, dP, p)
    m2 = pow(m, dQ, q)
    m1 ^= 1 << rng.randrange(m1.bit_length())      # один перекинутий біт
    h = (m1 - m2) * qInv % p
    return m2 + q * h

s_bad = sign_crt_faulty(msg, rng)
print(gcd(pow(s_bad, e, n) - msg, n) == q)         # True — за 0.15 мс
