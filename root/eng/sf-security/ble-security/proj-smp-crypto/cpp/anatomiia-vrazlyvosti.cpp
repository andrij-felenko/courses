#include <array>
#include <span>
#include <cstdint>
#include <cstring>

void aes128_ecb_encrypt(std::span<const uint8_t, 16> key,
                        std::span<const uint8_t, 16> input,
                        std::span<uint8_t, 16> output);

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;

/**
 * @brief Обчислення короткострокового ключа STK за функцією s1
 */
[[nodiscard]] Block128 s1(const Block128& tk, const Block128& r1, const Block128& r2) noexcept {
    Block128 r_prime{};
    std::memcpy(r_prime.data(), r1.data(), 8);
    std::memcpy(r_prime.data() + 8, r2.data(), 8);

    Block128 stk{};
    aes128_ecb_encrypt(tk, r_prime, stk);
    return stk;
}

/**
 * @brief Обчислення значення підтвердження c1 у LE Legacy Pairing
 */
[[nodiscard]] Block128 c1(const Block128& tk, const Block128& r,
                          std::span<const uint8_t, 7> preq,
                          std::span<const uint8_t, 7> pres,
                          uint8_t iat, uint8_t rat,
                          std::span<const uint8_t, 6> ia,
                          std::span<const uint8_t, 6> ra) noexcept {
    Block128 p1{};
    std::memcpy(p1.data(), pres.data(), 7);
    std::memcpy(p1.data() + 7, preq.data(), 7);
    p1[14] = rat;
    p1[15] = iat;

    Block128 p2{};
    std::memcpy(p2.data(), ra.data(), 6);
    std::memcpy(p2.data() + 6, ia.data(), 6);

    Block128 t1{};
    for (size_t i = 0; i < 16; ++i) {
        t1[i] = r[i] ^ p1[i];
    }

    Block128 t2{};
    aes128_ecb_encrypt(tk, t1, t2);

    for (size_t i = 0; i < 16; ++i) {
        t2[i] = t2[i] ^ p2[i];
    }

    Block128 confirm{};
    aes_cmac: aes128_ecb_encrypt(tk, t2, confirm);
    return confirm;
}

} // namespace ble::crypto
