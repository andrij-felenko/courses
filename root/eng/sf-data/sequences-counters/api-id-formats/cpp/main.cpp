#include <cstdint>
#include <chrono>

struct SnowflakeComponents {
    std::chrono::milliseconds timestamp;
    uint8_t datacenter_id;
    uint8_t worker_id;
    uint16_t sequence;
};

class SnowflakeCodec {
public:
    static constexpr uint64_t Epoch = 1288834974657ULL;

    [[nodiscard]] static constexpr uint64_t Pack(uint64_t timestamp_ms, uint8_t dc_id, uint8_t worker_id, uint16_t seq) noexcept {
        return ((timestamp_ms - Epoch) << 22)
             | ((static_cast<uint64_t>(dc_id) & 0x1F) << 17)
             | ((static_cast<uint64_t>(worker_id) & 0x1F) << 12)
             | (static_cast<uint64_t>(seq) & 0x0FFF);
    }

    [[nodiscard]] static constexpr SnowflakeComponents Unpack(uint64_t id) noexcept {
        return SnowflakeComponents{
            .timestamp = std::chrono::milliseconds{(id >> 22) + Epoch},
            .datacenter_id = static_cast<uint8_t>((id >> 17) & 0x1F),
            .worker_id = static_cast<uint8_t>((id >> 12) & 0x1F),
            .sequence = static_cast<uint16_t>(id & 0x0FFF)
        };
    }
};
