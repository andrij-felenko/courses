#include <array>
#include <span>
#include <cstdint>
#include <algorithm>

namespace crypto {

/* Бітове маскування (clamping) закритого скаляра X25519 за RFC 7748 */
constexpr void clamp_scalar(std::span<uint8_t, 32> scalar) noexcept {
    scalar[0]  &= 248; // Скидання бітів 0, 1, 2: кратність 8 (імунітет до кофактора)
    scalar[31] &= 127; // Скидання біта 255
    scalar[31] |= 64;  // Встановлення біта 254: фіксована бітова довжина
}

/* Перевірка публічного ключа на нульову точку за константний час */
[[nodiscard]] constexpr bool is_zero_public_key(std::span<const uint8_t, 32> pubkey) noexcept {
    uint8_t acc = 0;
    for (const uint8_t byte : pubkey) {
        acc |= byte;
    }
    return acc == 0;
}

} // namespace crypto
