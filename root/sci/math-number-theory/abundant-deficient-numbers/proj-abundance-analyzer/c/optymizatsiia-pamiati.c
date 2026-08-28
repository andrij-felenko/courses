#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct {
    uint32_t max_n;
    uint32_t* primes;
    uint32_t prime_count;
    uint32_t* min_prime;
    uint64_t* sigma;
    uint64_t* sigma_p;
} LinearSieve;

LinearSieve* create_sieve(uint32_t max_n) {
    LinearSieve* sieve = (LinearSieve*)malloc(sizeof(LinearSieve));
    if (!sieve) return NULL;

    sieve->max_n = max_n;
    sieve->primes = (uint32_t*)malloc(sizeof(uint32_t) * (max_n + 1));
    sieve->min_prime = (uint32_t*)calloc(max_n + 1, sizeof(uint32_t));
    sieve->sigma = (uint64_t*)malloc(sizeof(uint64_t) * (max_n + 1));
    sieve->sigma_p = (uint64_t*)malloc(sizeof(uint64_t) * (max_n + 1));
    sieve->prime_count = 0;

    if (!sieve->primes || !sieve->min_prime || !sieve->sigma || !sieve->sigma_p) {
        free(sieve->primes);
        free(sieve->min_prime);
        free(sieve->sigma);
        free(sieve->sigma_p);
        free(sieve);
        return NULL;
    }

    sieve->sigma[1] = 1;
    sieve->sigma_p[1] = 1;

    for (uint32_t i = 2; i <= max_n; ++i) {
        if (sieve->min_prime[i] == 0) {
            sieve->min_prime[i] = i;
            sieve->primes[sieve->prime_count++] = i;
            sieve->sigma[i] = i + 1;
            sieve->sigma_p[i] = i + 1;
        }

        for (uint32_t j = 0; j < sieve->prime_count; ++j) {
            uint32_t p = sieve->primes[j];
            if (p > sieve->min_prime[i] || (uint64_t)i * p > max_n) {
                break;
            }

            uint32_t target = i * p;
            sieve->min_prime[target] = p;

            if (i % p == 0) {
                sieve->sigma_p[target] = sieve->sigma_p[i] * p + 1;
                sieve->sigma[target] = (sieve->sigma[i] / sieve->sigma_p[i]) * sieve->sigma_p[target];
                break;
            } else {
                sieve->sigma_p[target] = p + 1;
                sieve->sigma[target] = sieve->sigma[i] * sieve->sigma[p];
            }
        }
    }

    return sieve;
}

void free_sieve(LinearSieve* sieve) {
    if (sieve) {
        free(sieve->primes);
        free(sieve->min_prime);
        free(sieve->sigma);
        free(sieve->sigma_p);
        free(sieve);
    }
}
