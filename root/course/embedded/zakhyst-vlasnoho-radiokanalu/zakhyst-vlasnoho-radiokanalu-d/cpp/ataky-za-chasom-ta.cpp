#include <span>
#include <cstdint>

// ✅ БЕЗПЕЧНО: порівняння за сталий час без розгалужень (C++)
[[nodiscard]] inline bool crypto_verify_16(
    std::span<const uint8_t, 16> a,
    std::span<const uint8_t, 16> b
) noexcept {
    uint8_t diff = 0;
    for (size_t i = 0; i < 16; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}
