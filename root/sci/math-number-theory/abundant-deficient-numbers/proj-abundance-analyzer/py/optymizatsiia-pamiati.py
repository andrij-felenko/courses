class LinearSieve:
    def __init__(self, max_n: int):
        self.max_n = max_n
        self.primes = []
        self.min_prime = [0] * (max_n + 1)
        self.sigma = [0] * (max_n + 1)
        self.sigma_p = [0] * (max_n + 1)

        self.sigma[1] = 1
        self.sigma_p[1] = 1

        for i in range(2, max_n + 1):
            if self.min_prime[i] == 0:
                self.min_prime[i] = i
                self.primes.append(i)
                self.sigma[i] = i + 1
                self.sigma_p[i] = i + 1

            for p in self.primes:
                if p > self.min_prime[i] or i * p > max_n:
                    break
                target = i * p
                self.min_prime[target] = p

                if i % p == 0:
                    self.sigma_p[target] = self.sigma_p[i] * p + 1
                    self.sigma[target] = (self.sigma[i] // self.sigma_p[i]) * self.sigma_p[target]
                    break
                else:
                    self.sigma_p[target] = p + 1
                    self.sigma[target] = self.sigma[i] * (p + 1)

    def is_abundant(self, n: int) -> bool:
        return n > 1 and self.sigma[n] > 2 * n
