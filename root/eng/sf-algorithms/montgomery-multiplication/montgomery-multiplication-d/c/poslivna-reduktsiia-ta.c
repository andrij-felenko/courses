#include <stdint.h>

/* Обчислення n0' = (-N[0]^(-1)) mod 2^64 за 6 кроків Гензеля */
uint64_t compute_n0_prime(uint64_t n0) {
    uint64_t inv = 1;
    for (int i = 0; i < 6; i++) {
        inv = inv * (2 - n0 * inv);
    }
    return (uint64_t)(-(int64_t)inv);
}
