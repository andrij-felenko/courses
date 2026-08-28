#include <type_traits>
#include <cstdint>

struct TelemetryPacket {
    uint32_t device_id;
    float    voltage;
    float    current;
    uint64_t timestamp_us;
};

static_assert(std::is_standard_layout_v<TelemetryPacket>, 
              "TelemetryPacket повинен мати Standard Layout для сумісності з C!");
