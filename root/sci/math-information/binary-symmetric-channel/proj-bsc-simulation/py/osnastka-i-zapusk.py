def theory(p):
    return 3*p**2 - 2*p**3            # = 3p²(1−p) + p³ — помилка ⟺ ≥2 перевороти з 3

def H(p):
    if p in (0.0, 1.0):
        return 0.0
    return -p*log2(p) - (1 - p)*log2(1 - p)

def capacity(p):
    return 1 - H(p)                   # стеля надійної швидкості, біт/символ
