#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

bool is_semiperfect_bitwise(uint64_t n, const uint64_t* divisors, size_t count) {
    size_t words = (n / 64) + 1;
    uint64_t* dp = (uint64_t*)calloc(words, sizeof(uint64_t));
    if (!dp) return false;

    dp[0] = 1ULL; // dp[0] = true (0-й біт)

    for (size_t i = 0; i < count; ++i) {
        uint64_t d = divisors[i];
        size_t word_shift = d / 64;
        uint64_t bit_shift = d % 64;

        for (size_t w = words - 1; w >= word_shift; --w) {
            size_t src = w - word_shift;
            uint64_t shifted = dp[src] << bit_shift;
            if (bit_shift > 0 && src > 0) {
                shifted |= (dp[src - 1] >> (64 - bit_shift));
            }
            dp[w] |= shifted;
        }

        if (dp[n / 64] & (1ULL << (n % 64))) {
            free(dp);
            return true;
        }
    }

    bool result = (dp[n / 64] & (1ULL << (n % 64))) != 0;
    free(dp);
    return result;
}

bool is_weird_number(uint64_t n) {
    if (n <= 1) return false;

    uint64_t sum_proper = 0;
    size_t capacity = 64;
    size_t count = 0;
    uint64_t* divisors = (uint64_t*)malloc(sizeof(uint64_t) * capacity);

    for (uint64_t d = 1; d * d <= n; ++d) {
        if (n % d == 0) {
            if (count >= capacity) {
                capacity *= 2;
                divisors = (uint64_t*)realloc(divisors, sizeof(uint64_t) * capacity);
            }
            divisors[count++] = d;
            sum_proper += d;

            uint64_t paired = n / d;
            if (paired != d && paired != n) {
                if (count >= capacity) {
                    capacity *= 2;
                    divisors = (uint64_t*)realloc(divisors, sizeof(uint64_t) * capacity);
                }
                divisors[count++] = paired;
                sum_proper += paired;
            }
        }
    }

    if (sum_proper <= n) {
        free(divisors);
        return false;
    }

    bool semiperfect = is_semiperfect_bitwise(n, divisors, count);
    free(divisors);

    return !semiperfect;
}
