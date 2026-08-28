#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define EULER_GAMMA 0.5772156649015328606
#define EXP_GAMMA   1.7810724179901979852

bool check_robin_inequality(uint64_t n, uint64_t sigma_n) {
    if (n <= 5040) return true; // Нерівність перевіряється лише для n > 5040

    double index = (double)sigma_n / (double)n;
    double log_log_n = log(log((double)n));
    double bound = EXP_GAMMA * log_log_n;

    return index < bound;
}
