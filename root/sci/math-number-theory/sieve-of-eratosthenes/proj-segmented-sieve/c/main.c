/* C11 implementation: Cache-aligned Segmented Sieve of Eratosthenes */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define L1_CACHE_BYTES 32768

typedef struct {
    uint32_t* primes;
    size_t count;
} PrimeArray;

/* Базове решето для знаходження простих чисел до limit */
static PrimeArray generate_base_primes(uint32_t limit) {
    PrimeArray result = {NULL, 0};
    if (limit < 2) return result;

    bool* is_prime = (bool*)malloc((limit + 1) * sizeof(bool));
    if (!is_prime) return result;

    memset(is_prime, true, (limit + 1) * sizeof(bool));
    is_prime[0] = is_prime[1] = false;

    for (uint32_t p = 2; p * p <= limit; ++p) {
        if (is_prime[p]) {
            for (uint32_t i = p * p; i <= limit; i += p) {
                is_prime[i] = false;
            }
        }
    }

    size_t count = 0;
    for (uint32_t i = 2; i <= limit; ++i) {
        if (is_prime[i]) count++;
    }

    result.primes = (uint32_t*)malloc(count * sizeof(uint32_t));
    result.count = count;

    if (!result.primes) {
        free(is_prime);
        result.count = 0;
        return result;
    }

    size_t idx = 0;
    for (uint32_t i = 2; i <= limit; ++i) {
        if (is_prime[i]) {
            result.primes[idx++] = i;
        }
    }

    free(is_prime);
    return result;
}

/* Сегментоване решето мовою C: повертає загальну кількість простих чисел π(N) */
uint64_t segmented_sieve_c(uint64_t n) {
    if (n < 2) return 0;

    uint32_t limit = (uint32_t)sqrt((double)n);
    PrimeArray base = generate_base_primes(limit);
    if (!base.primes && limit >= 2) return 0;

    uint64_t count = base.count; /* Включаємо базові прості */

    uint32_t segment_size = L1_CACHE_BYTES;
    uint8_t* segment = (uint8_t*)malloc(segment_size * sizeof(uint8_t));

    if (!segment) {
        free(base.primes);
        return 0;
    }

    /* Обробка інтервалу [limit + 1, n] блоками */
    for (uint64_t low = limit + 1; low <= n; low += segment_size) {
        uint64_t high = low + segment_size - 1;
        if (high > n) high = n;

        uint32_t current_size = (uint32_t)(high - low + 1);
        memset(segment, 1, current_size);

        for (size_t i = 0; i < base.count; ++i) {
            uint32_t p = base.primes[i];
            
            uint64_t start = ((low + p - 1) / p) * (uint64_t)p;
            uint64_t p_sq = (uint64_t)p * p;
            if (start < p_sq) start = p_sq;

            for (uint64_t j = start; j <= high; j += p) {
                segment[j - low] = 0;
            }
        }

        for (uint32_t i = 0; i < current_size; ++i) {
            if (segment[i]) {
                count++;
            }
        }
    }

    free(segment);
    free(base.primes);
    return count;
}

int main(void) {
    uint64_t N = 100000000; /* 100 мільйонів */
    printf("Обчислення простих чисел до N = %llu ...\n", (unsigned long long)N);
    uint64_t total_primes = segmented_sieve_c(N);
    printf("Знайдено простих чисел: %llu\n", (unsigned long long)total_primes);
    return 0;
}
