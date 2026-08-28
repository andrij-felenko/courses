#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

uint64_t sum_proper_divisors(uint64_t n) {
    if (n <= 1) return 0;
    uint64_t current_sigma = 1;
    uint64_t temp = n;

    for (uint64_t d = 2; d * d <= temp; ++d) {
        if (temp % d == 0) {
            uint64_t term_sum = 1;
            uint64_t p_power = 1;
            while (temp % d == 0) {
                p_power *= d;
                term_sum += p_power;
                temp /= d;
            }
            current_sigma *= term_sum;
        }
    }
    if (temp > 1) current_sigma *= (1 + temp);
    return current_sigma - n;
}

void trace_aliquot_sequence(uint64_t start, uint32_t max_steps) {
    uint64_t tortoise = start;
    uint64_t hare = start;

    printf("Aliquot sequence for %llu:\n%llu", (unsigned long long)start, (unsigned long long)start);

    for (uint32_t step = 0; step < max_steps; ++step) {
        tortoise = sum_proper_divisors(tortoise);
        hare = sum_proper_divisors(sum_proper_divisors(hare));

        printf(" -> %llu", (unsigned long long)tortoise);

        if (tortoise == 0) {
            printf(" [Terminated at 0]\n");
            return;
        }

        if (tortoise == hare && step > 0) {
            printf(" [Cycle detected]\n");
            return;
        }
    }
    printf(" [Limit reached]\n");
}
