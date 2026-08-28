#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

typedef enum {
    CLASS_DEFICIENT,
    CLASS_PERFECT,
    CLASS_ABUNDANT
} NumberClass;

typedef struct {
    uint64_t number;
    uint64_t sigma;
    uint64_t sum_proper;
    double index;
    NumberClass classification;
} AbundanceResult;

AbundanceResult analyze_number(uint64_t n) {
    AbundanceResult res;
    res.number = n;

    if (n <= 1) {
        res.sigma = n;
        res.sum_proper = 0;
        res.index = (double)n;
        res.classification = CLASS_DEFICIENT;
        return res;
    }

    uint64_t temp = n;
    uint64_t current_sigma = 1;

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

    if (temp > 1) {
        current_sigma *= (1 + temp);
    }

    res.sigma = current_sigma;
    res.sum_proper = current_sigma - n;
    res.index = (double)current_sigma / (double)n;

    if (res.sum_proper == n) {
        res.classification = CLASS_PERFECT;
    } else if (res.sum_proper > n) {
        res.classification = CLASS_ABUNDANT;
    } else {
        res.classification = CLASS_DEFICIENT;
    }

    return res;
}
