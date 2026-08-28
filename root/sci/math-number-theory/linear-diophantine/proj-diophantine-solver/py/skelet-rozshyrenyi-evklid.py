def ext_gcd(a, b):
    old_r, r = a, b
    old_s, s = 1, 0                 # коефіцієнт при a
    old_t, t = 0, 1                 # коефіцієнт при b
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t       # a·old_s + b·old_t == old_r == НСД
