#include <stdint.h>
#include <stdbool.h>

// Обчислення C(n, k) мультиплікативним методом для C (до n <= 62)
uint64_t ncr_multiplicative(uint32_t n, uint32_t k) {
    if (k > n) return 0;
    if (k == 0 || k == n) return 1;
    if (k > n - k) k = n - k;

    uint64_t res = 1;
    for (uint32_t i = 1; i <= k; ++i) {
        res = res * (n - k + i) / i;
    }
    return res;
}
