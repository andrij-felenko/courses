#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define THRESHOLD 2000000

static int64_t sum_mu_small[THRESHOLD + 1];
static int64_t memo_large[200000];
static bool visited_large[200000];
static int64_t target_N;

void precompute_sieve(int n) {
    int *primes = (int *)malloc((n + 1) * sizeof(int));
    int *mu = (int *)malloc((n + 1) * sizeof(int));
    bool *is_prime = (bool *)malloc((n + 1) * sizeof(bool));
    int cnt = 0;

    for (int i = 0; i <= n; ++i) is_prime[i] = true;
    mu[1] = 1;

    for (int i = 2; i <= n; ++i) {
        if (is_prime[i]) {
            primes[cnt++] = i;
            mu[i] = -1;
        }
        for (int j = 0; j < cnt && i * primes[j] <= n; ++j) {
            is_prime[i * primes[j]] = false;
            if (i % primes[j] == 0) {
                mu[i * primes[j]] = 0;
                break;
            }
            mu[i * primes[j]] = -mu[i];
        }
    }

    sum_mu_small[0] = 0;
    for (int i = 1; i <= n; ++i) {
        sum_mu_small[i] = sum_mu_small[i - 1] + mu[i];
    }

    free(primes);
    free(mu);
    free(is_prime);
}

int64_t get_sum_mu(int64_t n) {
    if (n <= THRESHOLD) return sum_mu_small[n];
    
    int idx = (int)(target_N / n);
    if (visited_large[idx]) return memo_large[idx];

    int64_t ans = 1; /* ∑ (μ * 1)(i) = ∑ ε(i) = 1 */
    for (int64_t l = 2, r; l <= n; l = r + 1) {
        r = n / (n / l);
        ans -= (r - l + 1) * get_sum_mu(n / l);
    }

    visited_large[idx] = true;
    memo_large[idx] = ans;
    return ans;
}

int main(void) {
    target_N = 1000000000LL; /* N = 10^9 */
    precompute_sieve(THRESHOLD);
    
    printf("M(10^9) = sum_{n<=10^9} mu(n) = %lld\n", (long long)get_sum_mu(target_N));
    return 0;
}
