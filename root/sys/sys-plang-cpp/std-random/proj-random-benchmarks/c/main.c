#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>

// Високоефективна реалізація LCG для мови C
typedef struct {
    uint64_t state;
} c_lcg_t;

static inline uint32_t c_lcg_next(c_lcg_t* rng) {
    rng->state = rng->state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (uint32_t)(rng->state >> 32);
}

int main(void) {
    c_lcg_t rng = { 1337ULL };
    const size_t N = 50000000;

    clock_t start = clock();
    uint32_t dummy = 0;
    for (size_t i = 0; i < N; ++i) {
        dummy += c_lcg_next(&rng);
    }
    clock_t end = clock();

    double seconds = (double)(end - start) / CLOCKS_PER_SEC;
    double mops = (N / seconds) / 1e6;

    printf("C LCG Benchmark: %.2f MOps/s (Checksum: %u)\n", mops, dummy);
    return 0;
}
