#include <span>
#include <cstdint>

bool constant_time_compare(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) return false;
    volatile uint8_t result = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        result |= static_cast<uint8_t>(a[i] ^ b[i]);
    }
    return result == 0;
}
