// Модулярне обчислення числа Каталана мовою C
#include <stdint.h>

static uint64_t power_mod(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return res;
}

static uint64_t mod_inverse(uint64_t n, uint64_t mod) {
    return power_mod(n, mod - 2, mod);
}

uint64_t catalan_mod(uint32_t n, uint64_t mod) {
    uint64_t res = 1;
    for (uint32_t i = 1; i <= n; ++i) {
        uint64_t num = (4 * (uint64_t)i - 2) % mod;
        uint64_t den_inv = mod_inverse(i + 1, mod);
        res = (res * num) % mod;
        res = (res * den_inv) % mod;
    }
    return res;
}
