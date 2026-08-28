def find_amicable_pairs_sieve(limit: int) -> list[tuple[int, int]]:
    """Знаходить усі унікальні дружні пари (a, b) у діапазоні 1 <= a < b <= limit

    за допомогою адитивного решета суми дільників.
    Часова складність: O(N log N), складність за пам'яттю: O(N).
    """
    # Створення та обнулення масиву сум дільників
    s = [0] * (limit + 1)

    # Адитивне генераційне решето
    for d in range(1, limit // 2 + 1):
        for m in range(2 * d, limit + 1, d):
            s[m] += d

    pairs = []
    # Відбір унікальних канонічних пар (a < b)
    for a in range(2, limit + 1):
        b = s[a]
        if a < b <= limit and s[b] == a:
            pairs.append((a, b))

    return pairs

if __name__ == "__main__":
    limit_val = 100_000
    found_pairs = find_amicable_pairs_sieve(limit_val)

    print(f"--- Знайдені дружні пари у діапазоні до {limit_val} ---")
    for idx, (a, b) in enumerate(found_pairs, 1):
        print(f"{idx:4}: ({a}, {b})")
    print(f"Усього знайдено пар: {len(found_pairs)}")
