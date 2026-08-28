#include <array>
#include <span>
#include <cstdint>
#include <cstring>

void aes128_ecb_encrypt(std::span<const uint8_t, 16> key,
                        std::span<const uint8_t, 16> input,
                        std::span<uint8_t, 16> output);

namespace ble::crypto {

using Key128 = std::array<uint8_t, 16>;
using Address48 = std::array<uint8_t, 6>;
using Hash24 = std::array<uint8_t, 3>;

/**
 * @brief Безпечна функція ah для генерації хешу RPA
 */
[[nodiscard]] Hash24 ah(const Key128& irk, std::span<const uint8_t, 3> prand) noexcept {
    Key128 plaintext{};
    Key128 ciphertext{};

    plaintext[0] = prand[0];
    plaintext[1] = prand[1];
    plaintext[2] = prand[2];

    aes128_ecb_encrypt(irk, plaintext, ciphertext);

    return {ciphertext[0], ciphertext[1], ciphertext[2]};
}

/**
 * @brief Перевірка належності адреси RPA збереженому ключу ідентичності IRK
 */
[[nodiscard]] bool resolve_rpa(const Address48& rpa, const Key128& irk) noexcept {
    /* Перевірка префіксу RPA: біти 7..6 старшого байта повинні дорівнювати 01b */
    if ((rpa[5] & 0xC0) != 0x40) {
        return false;
    }

    std::span<const uint8_t, 3> hash{rpa.data(), 3};
    std::span<const uint8_t, 3> prand{rpa.data() + 3, 3};

    const auto expected_hash = ah(irk, prand);
    return constant_time_compare(hash, expected_hash);
}

} // namespace ble::crypto
