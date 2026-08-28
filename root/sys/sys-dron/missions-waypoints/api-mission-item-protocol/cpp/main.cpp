#include <cstdint>
#include <cmath>
#include <expected>
#include <span>
#include <string_view>

#pragma pack(push, 1)
struct MissionItemIntPayload {
    float param1{0.0f};
    float param2{0.0f};
    float param3{0.0f};
    float param4{0.0f};
    int32_t x{0};
    int32_t y{0};
    float z{0.0f};
    uint16_t seq{0};
    uint16_t command{16};
    uint8_t target_system{1};
    uint8_t target_component{1};
    uint8_t frame{3}; // MAV_FRAME_GLOBAL_RELATIVE_ALT
    uint8_t current{0};
    uint8_t autocontinue{1};
    uint8_t mission_type{0};
};
#pragma pack(pop)

static_assert(sizeof(MissionItemIntPayload) == 38, "Payload size must strictly be 38 bytes");

enum class MissionResult : uint8_t {
    Accepted = 0,
    Error = 1,
    UnsupportedFrame = 2,
    UnsupportedCommand = 3,
    NoSpace = 4,
    InvalidParam1 = 6,
    InvalidParam2 = 7,
    InvalidCoords = 10,
    InvalidSequence = 13
};

class MissionItemValidator {
public:
    [[nodiscard]] static constexpr std::expected<void, MissionResult> validate(
        const MissionItemIntPayload& item, 
        uint16_t expected_seq
    ) noexcept {
        if (item.seq != expected_seq) {
            return std::unexpected(MissionResult::InvalidSequence);
        }

        const bool is_valid_frame = (item.frame == 0 || item.frame == 3 || item.frame == 6 || 
                                     item.frame == 10 || item.frame == 11);
        if (!is_valid_frame) {
            return std::unexpected(MissionResult::UnsupportedFrame);
        }

        // Перевірка геометричних параметрів радіуса прийняття та затримки
        if (item.command == 16) { // NAV_WAYPOINT
            if (item.param1 < 0.0f) {
                return std::unexpected(MissionResult::InvalidParam1);
            }
            if (item.param2 < 0.0f) {
                return std::unexpected(MissionResult::InvalidParam2);
            }
        }

        // Перевірка географічних меж: широта [-900000000..900000000], довгота [-1800000000..1800000000]
        constexpr int32_t LAT_LIMIT = 900'000'000;
        constexpr int32_t LON_LIMIT = 1'800'000'000;

        if (item.x < -LAT_LIMIT || item.x > LAT_LIMIT ||
            item.y < -LON_LIMIT || item.y > LON_LIMIT) {
            return std::unexpected(MissionResult::InvalidCoords);
        }

        if (std::isnan(item.z) || std::isnan(item.param1) || std::isnan(item.param2)) {
            return std::unexpected(MissionResult::InvalidCoords);
        }

        return {};
    }
};
