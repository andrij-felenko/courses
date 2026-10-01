#include <cstdint>
#include <cstddef>

namespace aht20 {

/**
 * @brief Обчислення контрольної суми CRC-8 для кадру AHT20 (попобітовий алгоритм).
 * @param data Вказівник на масив сирих байтів кадру.
 * @param len Довжина масиву.
 * @return Обчислена контрольна сума CRC-8.
 */
[[nodiscard]] constexpr std::uint8_t calculate_crc8_bitwise(const std::uint8_t *data, std::size_t len) noexcept {
    std::uint8_t crc = 0xFF; // Вектор ініціалізації
    
    for (std::size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (std::uint8_t bit = 0; bit < 8; ++bit) {
            if ((crc & 0x80) != 0) {
                crc = static_cast<std::uint8_t>((crc << 1) ^ 0x31);
            } else {
                crc = static_cast<std::uint8_t>(crc << 1);
            }
        }
    }
    return crc;
}

} // namespace aht20
