#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace crypto {

/**
 * Безпечне порівняння двох масивів фіксованої довжини в константному часі.
 */
template <size_t N>
[[nodiscard]] bool constant_time_equals(
    std::span<const uint8_t, N> a,
    std::span<const uint8_t, N> b) noexcept
{
    volatile uint8_t diff = 0;
    for (size_t i = 0; i < N; ++i) {
        diff = static_cast<uint8_t>(diff | (a[i] ^ b[i]));
    }
    return diff == 0;
}

/**
 * Верифікація HMAC-SHA256 підпису повідомлення з очищенням пам'яті.
 */
[[nodiscard]] bool verify_hmac_sha256(
    std::span<const uint8_t> key,
    std::span<const uint8_t> message,
    std::span<const uint8_t, 32> expected_tag) noexcept
{
    auto computed_tag = HmacSha256::sign(key, message);
    bool valid = constant_time_equals<32>(
        std::span<const uint8_t, 32>(computed_tag),
        expected_tag
    );
    computed_tag.fill(0);
    return valid;
}

} // namespace crypto
