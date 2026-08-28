#include <stdint.h>
#include <stdbool.h>

/* Безпечний підрахунок провідних нулів у C з ручною обробкою нуля */
static inline uint32_t safe_clz64(uint64_t x) {
    if (x == 0) {
        return 64;
    }
    return (uint32_t)__builtin_clzll(x);
}

/* Безпечне обчислення цілої частини логарифма log2 */
static inline int32_t safe_ilog2_64(uint64_t x) {
    if (x == 0) {
        return -1; /* Логарифм нуля невизначений */
    }
    return 63 - __builtin_clzll(x);
}

/* Перевірка степеня двійки */
static inline bool is_power_of_two(uint64_t x) {
    return x != 0 && (x & (x - 1)) == 0;
}
