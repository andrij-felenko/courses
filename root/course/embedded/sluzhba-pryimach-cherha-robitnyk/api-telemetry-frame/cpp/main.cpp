#include <cstdint>
#include <span>

class TelemetryCrc {
public:
    static uint16_t calculate(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (int i = 0; i < 8; ++i) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }

    static bool verify(std::span<const uint8_t, 24> frame) noexcept {
        const uint16_t expected_crc = (static_cast<uint16_t>(frame[22]) << 8) | frame[23];
        const uint16_t calculated_crc = calculate(frame.subspan<0, 22>());
        return expected_crc == calculated_crc;
    }
};
