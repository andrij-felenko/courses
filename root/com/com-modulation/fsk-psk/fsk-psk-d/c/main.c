#include <math.h>
#include <stdint.h>

// Біт на символ для сузір'я з M станами: log2(M).
static inline uint8_t bits_per_symbol(uint32_t M) {
    return (uint8_t)lround(log2((double)M));   // M=4 → 2, M=256 → 8
}

// Бітова швидкість (біт/с) із символьної (бод) і кількості станів сузір'я.
uint32_t bit_rate_bps(uint32_t baud, uint32_t M) {
    return baud * bits_per_symbol(M);
}

// 1 Мбод:  BPSK → 1e6,  QPSK → 2e6,  16-QAM → 4e6 біт/с
uint32_t r_bpsk = bit_rate_bps(1000000u, 2u);   // 1 000 000
uint32_t r_qpsk = bit_rate_bps(1000000u, 4u);   // 2 000 000
uint32_t r_qam  = bit_rate_bps(1000000u, 16u);  // 4 000 000
