namespace drm::crypto {

extern void aes128_decrypt_block(std::span<const uint8_t, 16> key,
                                 std::span<const uint8_t, 16> in,
                                 std::span<uint8_t, 16> out);

/**
 * Ідіоматичний C++20 Key Unwrap для 128-бітного ключа (приймає 24 байти, видає 16)
 */
std::optional<std::array<uint8_t, 16>> unwrap_key_128(
    std::span<const uint8_t, 16> kek,
    std::span<const uint8_t, 24> wrapped_key)
{
    constexpr size_t N = 2;
    std::array<uint8_t, 8> a{};
    std::memcpy(a.data(), wrapped_key.data(), 8);

    std::array<std::array<uint8_t, 8>, N> r{};
    std::memcpy(r[0].data(), wrapped_key.data() + 8, 8);
    std::memcpy(r[1].data(), wrapped_key.data() + 16, 8);

    for (int32_t j = 5; j >= 0; --j) {
        for (size_t i = N; i >= 1; --i) {
            uint64_t t = static_cast<uint64_t>(N * j + i);
            for (int k = 0; k < 8; ++k) {
                a[7 - k] ^= static_cast<uint8_t>((t >> (k * 8)) & 0xFF);
            }

            std::array<uint8_t, 16> b_in{};
            std::array<uint8_t, 16> b_out{};

            std::memcpy(b_in.data(), a.data(), 8);
            std::memcpy(b_in.data() + 8, r[i - 1].data(), 8);

            aes128_decrypt_block(kek, b_in, b_out);

            std::memcpy(a.data(), b_out.data(), 8);
            std::memcpy(r[i - 1].data(), b_out.data() + 8, 8);
        }
    }

    // Перевірка вектора цілісності
    if (a != DEFAULT_IV) {
        return std::nullopt; // Підроблені або пошкоджені дані
    }

    std::array<uint8_t, 16> plaintext_key{};
    std::memcpy(plaintext_key.data(), r[0].data(), 8);
    std::memcpy(plaintext_key.data() + 8, r[1].data(), 8);

    return plaintext_key;
}

} // namespace drm::crypto
