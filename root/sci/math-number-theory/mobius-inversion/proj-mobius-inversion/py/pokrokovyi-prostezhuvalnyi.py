def build_mobius_sieve(n: int) -> tuple[list[int], list[int]]:
    """
    Обчислює масив значень mu[1..N] та список простих чисел за час O(N).
    """
    mu = [0] * (n + 1)
    is_prime = [True] * (n + 1)
    primes = []

    mu[1] = 1
    is_prime[0] = is_prime[1] = False

    for i in range(2, n + 1):
        if is_prime[i]:
            primes.append(i)
            mu[i] = -1

        for p in primes:
            if p * i > n:
                break
            is_prime[p * i] = False
            if i % p == 0:
                mu[p * i] = 0
                break
            else:
                mu[p * i] = -mu[i]

    return mu, primes
