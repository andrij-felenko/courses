def count_coprime_pairs(n: int) -> int:
    """
    Обчислює кількість взаємно простих пар (i, j) таких, що 1 <= i, j <= N.
    Складність: O(N) на преобробку + O(√N) на обчислення суми.
    """
    mu, _ = build_mobius_sieve(n)

    # Побудова масиву префіксних сум M(x)
    pref_m = [0] * (n + 1)
    for i in range(1, n + 1):
        pref_m[i] = pref_m[i - 1] + mu[i]

    total_pairs = 0
    l = 1

    # Блокове підсумовування за O(√N) кроків
    while l <= n:
        k = n // l
        r = n // k
        block_sum_mu = pref_m[r] - pref_m[l - 1]
        total_pairs += block_sum_mu * (k * k)
        l = r + 1

    return total_pairs
