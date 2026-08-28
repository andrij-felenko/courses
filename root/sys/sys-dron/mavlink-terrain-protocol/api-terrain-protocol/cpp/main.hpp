#pragma once
#include <cstdint>
#include <array>
#include <span>

namespace mavlink {
namespace common {

// Повідомлення #133: TERRAIN_REQUEST
struct TerrainRequest {
    uint64_t mask{0};
    int32_t  lat{0};
    int32_t  lon{0};
    uint16_t grid_spacing{100};

    static constexpr uint8_t MSG_ID = 133;
    static constexpr uint8_t CRC_EXTRA = 6;
};

// Повідомлення #134: TERRAIN_DATA
struct TerrainData {
    int32_t  lat{0};
    int32_t  lon{0};
    uint16_t grid_spacing{100};
    uint8_t  gridbit{0};
    std::array<int16_t, 16> data{};

    static constexpr uint8_t MSG_ID = 134;
    static constexpr uint8_t CRC_EXTRA = 237;
};

// Повідомлення #135: TERRAIN_CHECK
struct TerrainCheck {
    int32_t lat{0};
    int32_t lon{0};

    static constexpr uint8_t MSG_ID = 135;
    static constexpr uint8_t CRC_EXTRA = 203;
};

// Повідомлення #136: TERRAIN_REPORT
struct TerrainReport {
    int32_t  lat{0};
    int32_t  lon{0};
    float    terrain_height{0.0f};
    float    current_height{0.0f};
    uint16_t spacing{100};
    uint16_t pending{0};
    uint16_t loaded{0};

    static constexpr uint8_t MSG_ID = 136;
    static constexpr uint8_t CRC_EXTRA = 1;
};

} // namespace common
} // namespace mavlink
