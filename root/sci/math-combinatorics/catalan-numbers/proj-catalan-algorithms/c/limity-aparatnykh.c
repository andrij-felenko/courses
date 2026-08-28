// Мультиплікативне обчислення мовою C з перевіркою переповнення uint64_t
#include <stdint.h>
#include <stdbool.h>

bool catalan_direct(uint32_t n, uint64_t* result) {
    if (n > 35) {
        // C_36 переповнює 64-бітне беззнакове число uint64_t (C_36 = 14,304,180,486,636,048,088 > 2^64-1)
        return false;
    }
    uint64_t res = 1;
    for (uint64_t i = 1; i <= n; ++i) {
        res = res * (4 * i - 2) / (i + 1);
    }
    *result = res;
    return true;
}
