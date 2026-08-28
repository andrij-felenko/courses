#include <cstdint>
#include <algorithm>
#include <optional>
#include <limits>

// Ідіоматична C++20 реалізація з constexpr та суворим контролем переповнення 64-бітного регістра
[[nodiscard]] constexpr std::optional<std::uint64_t> ncr_multiplicative(std::uint32_t n, std::uint32_t k) noexcept {
    if (k > n) return 0;
    if (k == 0 || k == n) return 1;
    k = std::min(k, n - k);

    std::uint64_t res = 1;
    for (std::uint32_t i = 1; i <= k; ++i) {
        std::uint64_t next_term = n - k + i;
        
        // Перевірка на переповнення перед множенням
        if (res > std::numeric_limits<std::uint64_t>::max() / next_term) {
            return std::nullopt; // Сигналізуємо про переповнення розрядної сітки
        }
        res = (res * next_term) / i;
    }
    return res;
}
