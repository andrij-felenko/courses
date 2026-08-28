#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>

namespace iso14443 {

class Crc16 {
public:
    static constexpr uint16_t INITIAL_VALUE = 0x6363;

    static uint16_t calculate(std::span<const uint8_t> data) noexcept {
        uint16_t w_crc = INITIAL_VALUE;

        for (uint8_t byte : data) {
            byte ^= static_cast<uint8_t>(w_crc & 0x00FF);
            byte ^= static_cast<uint8_t>(byte << 4);
            w_crc = (w_crc >> 8) ^
                    (static_cast<uint16_t>(byte) << 8) ^
                    (static_cast<uint16_t>(byte) << 3) ^
                    (static_cast<uint16_t>(byte) >> 4);
        }

        return w_crc;
    }

    static bool verify(std::span<const uint8_t> buffer) noexcept {
        if (buffer.size() < 2) return false;
        size_t payload_size = buffer.size() - 2;
        uint16_t calc_crc = calculate(buffer.subspan(0, payload_size));
        uint16_t recv_crc = static_cast<uint16_t>(buffer[payload_size]) |
                           (static_cast<uint16_t>(buffer[payload_size + 1]) << 8);
        return calc_crc == recv_crc;
    }

    static void append(std::vector<uint8_t>& buffer) {
        uint16_t crc = calculate(buffer);
        buffer.push_back(static_cast<uint8_t>(crc & 0xFF));
        buffer.push_back(static_cast<uint8_t>((crc >> 8) & 0xFF));
    }
};

} // namespace iso14443
