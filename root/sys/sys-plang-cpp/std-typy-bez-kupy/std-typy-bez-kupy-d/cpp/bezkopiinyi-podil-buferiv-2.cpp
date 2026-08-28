#include <span>
#include <cstdint>
#include <array>

struct DmaReceiver {
    std::array<uint8_t, 64> buffer{};
    std::size_t received_bytes{0};

    [[nodiscard]] std::span<const uint8_t> received_span() const noexcept {
        return std::span<const uint8_t>(buffer.data(), received_bytes);
    }
};

bool process_packet_cpp(std::span<const uint8_t> packet) noexcept {
    if (packet.size() < 4) {
        return false;
    }
    uint8_t packet_id = packet.front();
    std::span<const uint8_t> payload = packet.subspan(1, packet.size() - 3);
    std::span<const uint8_t, 2> crc_bytes = packet.last<2>();
    uint16_t expected_crc = static_cast<uint16_t>(crc_bytes[0] | (crc_bytes[1] << 8));

    (void)packet_id;
    (void)payload;
    (void)expected_crc;
    return true;
}
