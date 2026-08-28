// Динамічне програмування мовою C: обчислення масиву C[0...n]
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

uint64_t* catalan_dp_array(size_t n) {
    uint64_t* c = (uint64_t*)calloc(n + 1, sizeof(uint64_t));
    if (!c) return NULL;

    c[0] = 1;
    for (size_t i = 1; i <= n; ++i) {
        for (size_t j = 0; j < i; ++j) {
            c[i] += c[j] * c[i - 1 - j];
        }
    }
    return c;
}
