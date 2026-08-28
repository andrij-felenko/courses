#include <iostream>
#include <vector>
#include <unordered_map>
#include <cstdint>

class DuSieveMertens {
    int64_t N;
    int threshold;
    std::vector<int64_t> sum_mu_small;
    std::vector<int64_t> memo_large;
    std::vector<bool> visited_large;

public:
    explicit DuSieveMertens(int64_t n, int th = 2000000)
        : N(n), threshold(th), sum_mu_small(th + 1, 0),
          memo_large(200000, 0), visited_large(200000, false) {
        
        std::vector<int> primes;
        std::vector<int> mu(threshold + 1, 0);
        std::vector<bool> is_prime(threshold + 1, true);

        mu[1] = 1;
        for (int i = 2; i <= threshold; ++i) {
            if (is_prime[i]) {
                primes.push_back(i);
                mu[i] = -1;
            }
            for (int p : primes) {
                if (i * p > threshold) break;
                is_prime[i * p] = false;
                if (i % p == 0) {
                    mu[i * p] = 0;
                    break;
                }
                mu[i * p] = -mu[i];
            }
        }

        for (int i = 1; i <= threshold; ++i) {
            sum_mu_small[i] = sum_mu_small[i - 1] + mu[i];
        }
    }

    int64_t solve(int64_t n) {
        if (n <= threshold) return sum_mu_small[n];

        int idx = static_cast<int>(N / n);
        if (visited_large[idx]) return memo_large[idx];

        int64_t ans = 1; // sum_{i=1}^n (mu * 1)(i) = sum_{i=1}^n eps(i) = 1
        for (int64_t l = 2, r; l <= n; l = r + 1) {
            r = n / (n / l);
            ans -= (r - l + 1) * solve(n / l);
        }

        visited_large[idx] = true;
        memo_large[idx] = ans;
        return ans;
    }
};

int main() {
    constexpr int64_t N = 1000000000LL; // 10^9
    DuSieveMertens solver(N);
    std::cout << "M(10^9) = sum_{n<=10^9} mu(n) = " << solver.solve(N) << "\n";
    return 0;
}
