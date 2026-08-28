#include <cstddef>
#include <cstdint>
#include <span>

/* БЕЗПЕЧНО: Константний час порівняння з безпечним акумулятором розбіжностей */
[[nodiscard]] bool constant_time_memcmp(std::span<const uint8_t> a,
                                        std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }

    volatile uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= static_cast<uint8_t>(a[i] ^ b[i]);
    }

    return diff == 0;
}
