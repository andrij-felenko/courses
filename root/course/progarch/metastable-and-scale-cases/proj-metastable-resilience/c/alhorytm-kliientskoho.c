/* C Implementation: Exponential Backoff with Full Jitter */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

uint64_t calculate_backoff_full_jitter_ms(int attempt, uint64_t base_ms, uint64_t max_ms) {
    if (attempt <= 0) return 0;
    
    /* Calculate exponential limit: base * 2^(attempt-1) */
    uint64_t temp = base_ms << (attempt - 1);
    if (temp > max_ms || temp < base_ms) { /* Overflow check */
        temp = max_ms;
    }
    
    /* Full Jitter: Uniform random value in range [0, temp] */
    double random_factor = (double)rand() / (double)RAND_MAX;
    return (uint64_t)(random_factor * (double)temp);
}
