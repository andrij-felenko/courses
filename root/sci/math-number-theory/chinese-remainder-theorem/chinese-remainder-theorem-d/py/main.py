from math import prod

def crt(residues, moduli):
    """Розв'язати x ≡ residues[i] (mod moduli[i]) для попарно взаємно простих moduli."""
    N = prod(moduli)
    x = 0
    for a, n in zip(residues, moduli):
        Ni = N // n
        Mi = pow(Ni, -1, n)      # обернений; кине ValueError, якщо НСД(Ni, n) ≠ 1
        x += a * Ni * Mi
    return x % N

print(crt([2, 3, 2], [3, 5, 7]))     # 23 — задача Сунь-цзи
