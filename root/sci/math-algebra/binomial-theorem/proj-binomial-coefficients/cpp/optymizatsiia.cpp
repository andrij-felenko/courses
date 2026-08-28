#include <cstdint>
#include <vector>
#include <algorithm>

// Ідіоматичний C++20 з контейнером std::vector (автоматичне керування пам'яттю RAII)
[[nodiscard]] std::uint64_t ncr_pascal_dp(std::uint32_t n, std::uint32_t k) {
    if (k > n) return 0;
    k = std::min(k, n - k);

    std::vector<std::uint64_t> dp(k + 1, 0);
    dp[0] = 1;

    for (std::uint32_t i = 1; i <= n; ++i) {
        std::uint32_t limit = std::min(i, k);
        for (std::uint32_t j = limit; j > 0; --j) {
            dp[j] += dp[j - 1];
        }
    }
    return dp[k];
}
