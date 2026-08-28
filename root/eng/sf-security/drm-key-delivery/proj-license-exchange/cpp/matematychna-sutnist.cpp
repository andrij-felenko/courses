#include <array>
#include <span>
#include <cstdint>
#include <cstring>
#include <optional>

namespace drm::crypto {

// Фіксований IV для RFC 3394
constexpr std::array<uint8_t, 8> DEFAULT_IV = {
    0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6
};

extern void aes128_encrypt_block(std::span<const uint8_t, 16> key,
                                 std::span<const uint8_t, 16> in,
                                 std::span<uint8_t, 16> out);

/**
 * Ідіоматичний C++20 Key Wrap для 128-бітного ключа контенту (видає 24 байти)
 */
std::optional<std::array<uint8_t, 24>> wrap_key_128(
    std::span<const uint8_t, 16> kek,
    std::span<const uint8_t, 16> plaintext_key)
{
    constexpr size_t N = 2; // 2 блоки по 64 біти = 128 біт
    std::array<uint8_t, 8> a = DEFAULT_IV;
    std::array<std::array<uint8_t, 8>, N> r{};

    std::memcpy(r[0].data(), plaintext_key.data(), 8);
    std::memcpy(r[1].data(), plaintext_key.data() + 8, 8);

    for (uint32_t j = 0; j <= 5; ++j) {
        for (size_t i = 1; i <= N; ++i) {
            std::array<uint8_t, 16> b_in{};
            std::array<uint8_t, 16> b_out{};

            std::memcpy(b_in.data(), a.data(), 8);
            std::memcpy(b_in.data() + 8, r[i - 1].data(), 8);

            aes128_encrypt_block(kek, b_in, b_out);

            uint64_t t = static_cast<uint64_t>(N * j + i);
            std::memcpy(a.data(), b_out.data(), 8);
            for (int k = 0; k < 8; ++k) {
                a[7 - k] ^= static_cast<uint8_t>((t >> (k * 8)) & 0xFF);
            }

            std::memcpy(r[i - 1].data(), b_out.data() + 8, 8);
        }
    }

    std::array<uint8_t, 24> wrapped{};
    std::memcpy(wrapped.data(), a.data(), 8);
    std::memcpy(wrapped.data() + 8, r[0].data(), 8);
    std::memcpy(wrapped.data() + 16, r[1].data(), 8);

    return wrapped;
}

} // namespace drm::crypto
