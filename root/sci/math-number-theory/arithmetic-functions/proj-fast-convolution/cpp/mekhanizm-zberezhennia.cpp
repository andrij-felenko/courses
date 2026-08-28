#include <iostream>
#include <vector>
#include <cstdint>

struct MultiplicativeSieve {
    std::vector<int> primes;
    std::vector<int> mu;
    std::vector<int> phi;

    explicit MultiplicativeSieve(int n) : mu(n + 1), phi(n + 1) {
        std::vector<int> min_pow(n + 1, 0);
        mu[1] = 1;
        phi[1] = 1;

        primes.reserve(n / 10);
        for (int i = 2; i <= n; ++i) {
            if (min_pow[i] == 0) {
                primes.push_back(i);
                mu[i] = -1;
                phi[i] = i - 1;
                min_pow[i] = i;
            }
            for (int p : primes) {
                if (p * i > n) break;
                int next = i * p;
                if (i % p == 0) {
                    mu[next] = 0;
                    phi[next] = phi[i] * p;
                    min_pow[next] = min_pow[i] * p;
                    break;
                }
                mu[next] = mu[i] * mu[p];
                phi[next] = phi[i] * phi[p];
                min_pow[next] = p;
            }
        }
    }
};

int main() {
    constexpr int n = 20;
    MultiplicativeSieve sieve(n);

    std::cout << "n\tmu(n)\tphi(n)\n";
    for (int i = 1; i <= n; ++i) {
        std::cout << i << "\t" << sieve.mu[i] << "\t" << sieve.phi[i] << "\n";
    }
    return 0;
}
