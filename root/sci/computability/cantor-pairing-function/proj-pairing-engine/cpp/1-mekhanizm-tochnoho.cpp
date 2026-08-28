#include <cstdint>
#include <optional>
#include <vector>
#include <span>
#include <concepts>
#include <bit>

namespace pairing {

/* C++20 constexpr-сумісний точний цілочисельний квадратний корінь.
   Використовує std::countl_zero для миттєвого знаходження старшого розряду. */
[[nodiscard]] constexpr uint64_t isqrt64(uint64_t n) noexcept {
    if (n == 0) return 0;

    uint64_t root = 0;
    const int lz = std::countl_zero(n);
    const int shift = (63 - lz) & ~1; /* Округлення вниз до парного степеня */
    uint64_t bit = static_cast<uint64_t>(1) << shift;

    while (bit != 0) {
        if (n >= root + bit) {
            n -= root + bit;
            root = (root >> 1) + bit;
        } else {
            root >>= 1;
        }
        bit >>= 2;
    }

    return root;
}

} // namespace pairing
