#include <span>
#include <vector>
#include <expected>
#include <print>
#include <cstdint>

struct TelemetryPacket {
    double timestamp{0.0};
    float value{0.0f};
    std::uint32_t status_flags{0};
};

enum class FilterError : std::uint8_t {
    EmptyInput,
    BufferCorrupted
};

[[nodiscard]] std::expected<std::vector<TelemetryPacket>, FilterError> 
filter_active_packets(std::span<const TelemetryPacket> input) noexcept 
{
    if (input.empty()) {
        return std::unexpected(FilterError::EmptyInput);
    }

    std::vector<TelemetryPacket> active_packets;
    active_packets.reserve(input.size());

    for (const auto& packet : input) {
        if ((packet.status_flags & 0x01U) != 0U) {
            active_packets.push_back(packet);
        }
    }

    std::println("Extracted {} active packets safely", active_packets.size());
    return active_packets;
}
