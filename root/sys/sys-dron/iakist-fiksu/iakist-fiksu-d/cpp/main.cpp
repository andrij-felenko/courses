#include <cstdint>
#include <optional>

namespace drone::gnss {

enum class FixType : uint8_t {
    NoFix = 0,
    DeadReckoningOnly = 1,
    Fix2D = 2,
    Fix3D = 3,
    GNSSPlusDeadReckoning = 4,
    TimeOnly = 5
};

struct UbxPvtSnapshot {
    FixType  fix_type{FixType::NoFix};
    uint8_t  flags{0};
    uint8_t  satellites_used{0};
    int32_t  longitude_e7{0};
    int32_t  latitude_e7{0};
    int32_t  height_msl_mm{0};
    uint32_t h_accuracy_mm{0};
    uint32_t v_accuracy_mm{0};
    uint16_t pdop_scaled{0};

    [[nodiscard]] constexpr bool isFixOk() const noexcept {
        return (flags & 0x01) != 0;
    }

    [[nodiscard]] constexpr float pdop() const noexcept {
        return static_cast<float>(pdop_scaled) * 0.01f;
    }

    [[nodiscard]] constexpr float horizontalAccuracyMeters() const noexcept {
        return static_cast<float>(h_accuracy_mm) * 0.001f;
    }
};

struct HealthStatus {
    bool  is_healthy{false};
    bool  is_armable{false};
    float estimated_hdop{99.9f};
    float horizontal_accuracy_m{999.0f};
};

[[nodiscard]] inline HealthStatus evaluateHealth(const UbxPvtSnapshot& pvt) noexcept {
    HealthStatus status{};
    status.horizontal_accuracy_m = pvt.horizontalAccuracyMeters();
    const float pdop_val = pvt.pdop();
    status.estimated_hdop = pdop_val * 0.65f;

    if (pvt.isFixOk() && static_cast<uint8_t>(pvt.fix_type) >= 3 && pvt.satellites_used >= 6) {
        status.is_healthy = true;
    }

    if (status.is_healthy && pvt.satellites_used >= 8 && pdop_val <= 2.5f && status.horizontal_accuracy_m <= 2.0f) {
        status.is_armable = true;
    }

    return status;
}

} // namespace drone::gnss
