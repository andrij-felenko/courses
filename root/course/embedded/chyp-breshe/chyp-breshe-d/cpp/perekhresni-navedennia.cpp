#include <cstdint>
#include <span>
#include <optional>

class SensirionPacket {
public:
    static constexpr uint8_t POLYNOMIAL = 0x31;
    static constexpr uint8_t INITIAL_CRC = 0xFF;

    static constexpr uint8_t calculate_crc8(std::span<const uint8_t> data) noexcept {
        uint8_t crc = INITIAL_CRC;
        for (const auto byte : data) {
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

    static constexpr std::optional<uint16_t> unpack(std::span<const uint8_t, 3> raw_packet) noexcept {
        const auto payload = raw_packet.subspan<0, 2>();
        const uint8_t expected_crc = raw_packet[2];

        if (calculate_crc8(payload) != expected_crc) {
            return std::nullopt; // Помилка контрольної суми
        }

        return static_cast<uint16_t>((static_cast<uint16_t>(raw_packet[0]) << 8) |
                                      static_cast<uint16_t>(raw_packet[1]));
    }
};
