#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int* mu;
    int* primes;
    int prime_count;
} mobius_sieve_t;

mobius_sieve_t create_mobius_sieve(int n) {
    mobius_sieve_t res;
    res.mu = (int*)malloc((n + 1) * sizeof(int));
    res.primes = (int*)malloc((n + 1) * sizeof(int));
    bool* is_prime = (bool*)malloc((n + 1) * sizeof(bool));
    res.prime_count = 0;

    for (int i = 0; i <= n; i++) {
        is_prime[i] = true;
        res.mu[i] = 0;
    }
    res.mu[1] = 1;
    is_prime[0] = is_prime[1] = false;

    for (int i = 2; i <= n; i++) {
        if (is_prime[i]) {
            res.primes[res.prime_count++] = i;
            res.mu[i] = -1;
        }
        for (int j = 0; j < res.prime_count; j++) {
            int p = res.primes[j];
            if (p * i > n) break;
            is_prime[p * i] = false;
            if (i % p == 0) {
                res.mu[p * i] = 0;
                break;
            } else {
                res.mu[p * i] = -res.mu[i];
            }
        }
    }

    free(is_prime);
    return res;
}

void free_mobius_sieve(mobius_sieve_t* sieve) {
    free(sieve->mu);
    free(sieve->primes);
    sieve->mu = NULL;
    sieve->primes = NULL;
}
