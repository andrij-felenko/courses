def is_prime(n):                       # показник теж мусить бути простим
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True

def lucas_lehmer(p):                    # p — непарне просте
    M = (1 << p) - 1                    # Mₚ = 2ᵖ − 1
    s = 4
    for _ in range(p - 2):
        s = (s * s - 2) % M            # серце тесту
    return s == 0

for p in range(3, 2300):
    if is_prime(p) and lucas_lehmer(p):
        perfect = (1 << (p - 1)) * ((1 << p) - 1)
        print(p, "→ досконале =", perfect)
