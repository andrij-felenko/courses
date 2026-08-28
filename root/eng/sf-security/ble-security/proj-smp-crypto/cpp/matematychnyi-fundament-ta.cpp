#include <span>
#include <cstdint>
#include <cstddef>

namespace ble::crypto {

/**
 * @brief Безпечне порівняння байтових послідовностей за константний час
 */
[[nodiscard]] bool constant_time_compare(std::span<const uint8_t> a,
                                         std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }

    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }

    return diff == 0;
}

} // namespace ble::crypto
