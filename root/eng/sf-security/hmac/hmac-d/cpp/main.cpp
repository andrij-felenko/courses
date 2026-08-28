#include <cstddef>
#include <cstdint>
#include <span>

namespace crypto {

/**
 * Константне порівняння двох бінарних масивів для захисту від Side-Channel атак.
 */
[[nodiscard]] bool constant_time_equals(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }

    const volatile uint8_t* p1 = a.data();
    const volatile uint8_t* p2 = b.data();
    uint8_t diff = 0;

    for (size_t i = 0; i < a.size(); ++i) {
        diff |= static_cast<uint8_t>(p1[i] ^ p2[i]);
    }

    return diff == 0;
}

} // namespace crypto
