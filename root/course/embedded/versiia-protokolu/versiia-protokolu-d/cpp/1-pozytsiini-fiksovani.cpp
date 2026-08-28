#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <optional>

#pragma pack(push, 1)
struct TelemetryV1 {
    uint16_t voltage_mv;  // Offset 0..1
    int32_t  current_ma;  // Offset 2..5
    uint16_t status_bits; // Offset 6..7
};

struct TelemetryV2 {
    uint16_t voltage_mv;
    int32_t  current_ma;
    uint16_t status_bits;
    int16_t  temperature_c_x100{-32768};
    uint32_t system_uptime_sec{0};
};
#pragma pack(pop)

class TelemetryDecoder {
public:
    static std::optional<TelemetryV2> decode(std::span<const uint8_t> payload) {
        if (payload.size() < sizeof(TelemetryV1)) {
            return std::nullopt;
        }

        TelemetryV2 result{};
        const size_t bytes_to_copy = std::min(payload.size(), sizeof(TelemetryV2));
        std::memcpy(&result, payload.data(), bytes_to_copy);

        return result;
    }
};
