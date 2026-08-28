#include <cstdint>
#include <cstddef>
#include <span>

namespace mipi::csi2 {

// Побайтовий розрахунок CRC-16-CCITT для перевірки кінцевика CSI-2
constexpr uint16_t crc16_update(uint16_t crc, uint8_t byte) noexcept {
    crc ^= static_cast<uint16_t>(static_cast<uint16_t>(byte) << 8);
    for (int i = 0; i < 8; ++i) {
        if (crc & 0x8000) {
            crc = static_cast<uint16_t>((crc << 1) ^ 0x1021);
        } else {
            crc = static_cast<uint16_t>(crc << 1);
        }
    }
    return crc;
}

// Пакетний розрахунок контрольної суми над усім масивом Payload
constexpr uint16_t calculate_payload_crc(std::span<const uint8_t> payload) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : payload) {
        crc = crc16_update(crc, byte);
    }
    return crc;
}

} // namespace mipi::csi2
