p, q = 61, 53
n, e = p * q, 17                 # n = 3233
phi = (p - 1) * (q - 1)          # 3120
lam = lcm(p - 1, q - 1)          # 780
d_phi = pow(e, -1, phi)          # 2753
d_lam = pow(e, -1, lam)          # 413

msg = 123
c = pow(msg, e, n)
assert pow(c, d_lam, n) == msg
assert pow(c, d_phi, n) == msg   # обидва показники розшифровують
