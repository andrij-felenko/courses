#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// Динамічне програмування для C(n, k) з безпечним динамічним виділенням пам'яті
uint64_t ncr_pascal_dp(uint32_t n, uint32_t k) {
    if (k > n) return 0;
    if (k > n - k) k = n - k;

    uint64_t *dp = (uint64_t *)calloc(k + 1, sizeof(uint64_t));
    if (!dp) return 0; // Перевірка виділення пам'яті
    dp[0] = 1;

    for (uint32_t i = 1; i <= n; ++i) {
        uint32_t limit = i < k ? i : k;
        for (uint32_t j = limit; j > 0; --j) {
            dp[j] += dp[j - 1];
        }
    }

    uint64_t result = dp[k];
    free(dp);
    return result;
}
