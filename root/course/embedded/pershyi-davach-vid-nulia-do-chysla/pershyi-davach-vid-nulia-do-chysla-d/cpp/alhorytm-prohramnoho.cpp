#include <cstdint>
#include <cstddef>
#include <span>

namespace sensor {

inline constexpr uint8_t SHT3X_CRC8_POLYNOMIAL = 0x31;
inline constexpr uint8_t SHT3X_CRC8_INIT       = 0xFF;

[[nodiscard]] constexpr uint8_t calculate_crc8(std::span<const uint8_t> data) noexcept {
    uint8_t crc = SHT3X_CRC8_INIT;
    for (const uint8_t byte : data) {
        crc ^= byte;
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 0x80) {
                crc = static_cast<uint8_t>((crc << 1) ^ SHT3X_CRC8_POLYNOMIAL);
            } else {
                crc = static_cast<uint8_t>(crc << 1);
            }
        }
    }
    return crc;
}

[[nodiscard]] constexpr bool validate_crc(std::span<const uint8_t, 2> data, uint8_t expected_crc) noexcept {
    return calculate_crc8(data) == expected_crc;
}

} // namespace sensor
