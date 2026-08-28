#include <cstdint>
#include <cstring>
#include <span>
#include <optional>

struct TelemetryPacket {
    uint16_t magic;
    uint16_t sensor_id;
    float temperature;
    float pressure;
    uint32_t checksum;
};

std::optional<TelemetryPacket> parse_telemetry(std::span<const std::byte> buffer) noexcept {
    if (buffer.size() < sizeof(TelemetryPacket)) {
        return std::nullopt;
    }

    TelemetryPacket packet{};
    std::memcpy(&packet, buffer.data(), sizeof(TelemetryPacket));

    if (packet.magic != 0xAA55) {
        return std::nullopt;
    }

    return packet;
}
