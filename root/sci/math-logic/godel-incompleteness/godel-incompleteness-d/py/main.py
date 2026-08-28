SYMBOLS = {"0": 1, "s": 2, "=": 3, "(": 4, ")": 5, "¬": 6, "∨": 7, "∀": 8, "x": 9}
BACK = {code: sym for sym, code in SYMBOLS.items()}

def primes(n):
    """Перші n простих — основи, у показники яких сядуть коди символів."""
    out, k = [], 2
    while len(out) < n:
        if all(k % p for p in out):
            out.append(k)
        k += 1
    return out

def encode(formula):
    """Формула (рядок символів) → одне натуральне число."""
    codes = [SYMBOLS[s] for s in formula]
    g = 1
    for p, c in zip(primes(len(codes)), codes):
        g *= p ** c                  # i-й символ сидить у показнику i-го простого
    return g

def decode(g):
    """Число → формула. Розклад на прості однозначний, тож дорога назад одна."""
    out = []
    for p in primes(64):             # із запасом: формула коротша за 64 символи
        if g == 1:
            break
        c = 0
        while g % p == 0:            # скільки разів p ділить g — це й є код символу
            g //= p
            c += 1
        if c == 0:                   # діра в простих: число не кодує формулу
            raise ValueError("не код формули")
        out.append(BACK[c])
    return "".join(out)

encode("0=0")                  # 270
decode(270)                    # '0=0'
encode("ss0=ss0")              # 21462861420
decode(21462861420)            # 'ss0=ss0'
