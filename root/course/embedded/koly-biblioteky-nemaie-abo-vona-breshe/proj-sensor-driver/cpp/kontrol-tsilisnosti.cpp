#include <cstdint>
#include <cstddef>
#include <span>

namespace driver {

/* Побітовий розрахунок CRC-8 у стандарті C++20 */
[[nodiscard]] constexpr uint8_t compute_crc8_fast(std::span<const uint8_t> data) noexcept {
    constexpr uint8_t POLYNOMIAL = 0x31;
    uint8_t crc = 0xFF;
    for (const uint8_t byte : data) {
        crc ^= byte;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if ((crc & 0x80) != 0) {
                crc = static_cast<uint8_t>((crc << 1) ^ POLYNOMIAL);
            } else {
                crc = static_cast<uint8_t>(crc << 1);
            }
        }
    }
    return crc;
}

} // namespace driver
