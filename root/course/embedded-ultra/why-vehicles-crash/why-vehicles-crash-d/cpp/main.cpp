#include <cstdint>
#include <functional>

enum class FailsafeMode : uint8_t {
    None = 0,
    SensorDegraded,
    ReturnToHome,
    EmergencyLand,
    CriticalTerminate
};

struct FlightTelemetry {
    uint32_t last_rc_tick_ms{0};
    uint32_t last_imu_tick_ms{0};
    float vbat_volts{16.8f};
    float tilt_roll_deg{0.0f};
    float tilt_pitch_deg{0.0f};
    bool gps_valid{true};
};

class FailsafeController {
public:
    static constexpr uint32_t kRcTimeoutMs = 1500;
    static constexpr uint32_t kImuTimeoutMs = 40;
    static constexpr float kCriticalVoltage4S = 13.2f;
    static constexpr float kMaxTiltAngleDeg = 75.0f;

    [[nodiscard]] FailsafeMode evaluate(const FlightTelemetry& telem, uint32_t now_ms) const noexcept {
        const uint32_t rc_dt = now_ms - telem.last_rc_tick_ms;
        const uint32_t imu_dt = now_ms - telem.last_imu_tick_ms;

        // 1. Негайне аварійне глушіння при перекиданні або втраті датчиків кута
        if (imu_dt > kImuTimeoutMs ||
            telem.tilt_roll_deg > kMaxTiltAngleDeg || telem.tilt_roll_deg < -kMaxTiltAngleDeg ||
            telem.tilt_pitch_deg > kMaxTiltAngleDeg || telem.tilt_pitch_deg < -kMaxTiltAngleDeg) {
            return FailsafeMode::CriticalTerminate;
        }

        // 2. Критичний розряд батареї
        if (telem.vbat_volts < kCriticalVoltage4S) {
            return FailsafeMode::EmergencyLand;
        }

        // 3. Втрата радіоканалу зв'язку
        if (rc_dt > kRcTimeoutMs) {
            return telem.gps_valid ? FailsafeMode::ReturnToHome : FailsafeMode::EmergencyLand;
        }

        return FailsafeMode::None;
    }

    // Апаратне відновлення шини I2C
    static bool recover_i2c_bus(const std::function<void(bool)>& scl_set,
                               const std::function<bool()>& sda_read,
                               const std::function<void(uint32_t)>& delay_fn) noexcept {
        for (uint8_t i = 0; i < 9; ++i) {
            if (sda_read()) {
                return true; // Лінія SDA вільна
            }
            scl_set(false);
            delay_fn(5);
            scl_set(true);
            delay_fn(5);
        }
        return sda_read();
    }
};
