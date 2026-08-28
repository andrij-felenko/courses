#include <cstdint>
#include <span>
#include <array>

namespace sensirion::scd30 {

constexpr uint8_t Crc8Polynomial = 0x31;
constexpr uint8_t Crc8Init = 0xFF;

/**
 * @brief Розрахунок контрольної суми CRC-8 на етапі компіляції або виконання.
 */
[[nodiscard]] constexpr uint8_t compute_crc8(std::span<const uint8_t> data) noexcept {
    uint8_t crc = Crc8Init;
    for (const uint8_t byte : data) {
        crc ^= byte;
        for (uint8_t bit = 8; bit > 0; --bit) {
            if ((crc & 0x80) != 0) {
                crc = static_cast<uint8_t>((crc << 1) ^ Crc8Polynomial);
            } else {
                crc = static_cast<uint8_t>(crc << 1);
            }
        }
    }
    return crc;
}

/**
 * @brief Верифікація отриманого слова даних та контрольного байта.
 */
[[nodiscard]] constexpr bool check_crc8(std::span<const uint8_t, 2> word, uint8_t expected_crc) noexcept {
    return compute_crc8(word) == expected_crc;
}

} // namespace sensirion::scd30
