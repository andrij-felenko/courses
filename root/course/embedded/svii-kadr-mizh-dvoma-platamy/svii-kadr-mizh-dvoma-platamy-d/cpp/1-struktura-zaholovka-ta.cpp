#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <algorithm>

namespace protocol {

constexpr size_t MaxPayloadSize = 128;

#pragma pack(push, 1)
struct FrameHeader {
    uint8_t  msg_id{0};       // Ідентифікатор типу повідомлення
    uint8_t  seq_num{0};      // Порядковий номер кадру (0..255)
    uint16_t payload_len{0};  // Довжина корисних даних (Little-Endian)
};
#pragma pack(pop)

constexpr size_t MaxPacketSize  = sizeof(FrameHeader) + MaxPayloadSize + sizeof(uint16_t);
constexpr size_t MaxEncodedSize = MaxPacketSize + (MaxPacketSize / 254) + 2;

// Обчислення CRC-16-CCITT через constexpr функцію
constexpr uint16_t crc16_update(uint16_t crc, uint8_t data) noexcept {
    data ^= static_cast<uint8_t>(crc >> 8);
    data ^= static_cast<uint8_t>(data >> 4);
    return static_cast<uint16_t>((crc << 8) ^ 
           (static_cast<uint16_t>(data) << 12) ^ 
           (static_cast<uint16_t>(data) << 5) ^ 
           static_cast<uint16_t>(data));
}

inline uint16_t crc16_calculate(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : data) {
        crc = crc16_update(crc, byte);
    }
    return crc;
}

} // namespace protocol
