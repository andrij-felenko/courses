def coprime_count(N: int, primes: list[int]) -> int:
    total = 0
    for mask in range(1 << len(primes)):
        prod, over = 1, False
        for i, pi in enumerate(primes):
            if (mask >> i) & 1:
                if pi > N // prod:          # добуток перевищив би N → далі ⌊N/добуток⌋ = 0
                    over = True             # тут це ЛИШЕ оптимізація: цілі Python необмежені,
                    break                   # переповнення не буває, обриваємо марне множення
                prod *= pi
        term = 0 if over else N // prod
        total += -term if bin(mask).count("1") & 1 else term   # знак за парністю розміру
    return total


def divisible_by_any(N: int, primes: list[int]) -> int:
    return N - coprime_count(N, primes)
