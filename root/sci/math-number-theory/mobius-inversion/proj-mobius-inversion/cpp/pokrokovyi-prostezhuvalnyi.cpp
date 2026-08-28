#include <vector>
#include <cstdint>
#include <iostream>

struct MobiusSieve {
    std::vector<int32_t> mu;
    std::vector<int32_t> primes;

    explicit MobiusSieve(size_t n) : mu(n + 1, 0) {
        std::vector<bool> is_prime(n + 1, true);
        mu[1] = 1;
        is_prime[0] = is_prime[1] = false;

        primes.reserve(n / 10);

        for (size_t i = 2; i <= n; ++i) {
            if (is_prime[i]) {
                primes.push_back(static_cast<int32_t>(i));
                mu[i] = -1;
            }
            for (int32_t p : primes) {
                if (p * i > n) break;
                is_prime[p * i] = false;
                if (i % p == 0) {
                    mu[p * i] = 0;
                    break;
                } else {
                    mu[p * i] = -mu[i];
                }
            }
        }
    }
};
