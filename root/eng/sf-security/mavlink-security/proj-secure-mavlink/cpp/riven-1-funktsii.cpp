#include <cstdint>
#include <cstddef>
#include <span>
#include <algorithm>

namespace mavlink_sec {

// Порівняння спанів пам'яті за строго постійний час у C++
[[nodiscard]] int secureMemcmp(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return -1;
    }

    uint8_t result = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        result |= (a[i] ^ b[i]);
    }

    return (result == 0) ? 0 : -1;
}

// Гарантоване очищення пам'яті з використанням volatile-вказівника
void secureZeroize(std::span<uint8_t> buffer) noexcept {
    volatile uint8_t* p = const_cast<volatile uint8_t*>(buffer.data());
    for (size_t i = 0; i < buffer.size(); ++i) {
        p[i] = 0;
    }
}

} // namespace mavlink_sec
