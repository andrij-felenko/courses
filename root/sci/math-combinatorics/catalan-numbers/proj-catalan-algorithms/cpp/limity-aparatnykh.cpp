// Мультиплікативне обчислення мовою C++ з використанням std::optional
#include <cstdint>
#include <optional>

std::optional<std::uint64_t> compute_catalan_single(std::uint32_t n) noexcept {
    if (n > 35) {
        return std::nullopt; // Межа 64-бітного беззнакового типом uint64_t
    }
    std::uint64_t res = 1;
    for (std::uint64_t i = 1; i <= n; ++i) {
        res = res * (4 * i - 2) / (i + 1);
    }
    return res;
}
