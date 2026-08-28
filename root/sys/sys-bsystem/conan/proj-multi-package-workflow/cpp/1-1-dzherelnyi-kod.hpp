#pragma once

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>
#include <span>

namespace telemetry {

struct SensorRecord {
    uint32_t sensor_id{0};
    uint64_t timestamp_ns{0};
    double value{0.0};
};

class PacketEncoder {
public:
    explicit PacketEncoder(std::string_view channel_name);

    [[nodiscard]] std::vector<uint8_t> encode(std::span<const SensorRecord> records) const;
    [[nodiscard]] std::string_view channel_name() const noexcept;

private:
    std::string channel_name_;
};

} // namespace telemetry
