#include <cstdint>
#include <functional>

enum class FailsafeState : uint8_t {
    Normal = 0,
    SensorDegraded,
    AutoRth,
    EmergencyDescent,
    CriticalTerminate
};

struct VehicleHealth {
    uint32_t last_rc_packet_ms{0};
    uint32_t last_gps_fix_ms{0};
    uint32_t last_imu_sample_ms{0};
    float battery_voltage_v{16.8f};
    float roll_deg{0.0f};
    float pitch_deg{0.0f};
    bool i2c_bus_healthy{true};
};

class FailsafeManager {
public:
    static constexpr uint32_t kRcTimeoutMs = 1500;
    static constexpr uint32_t kGpsTimeoutMs = 3000;
    static constexpr uint32_t kImuTimeoutMs = 40;
    static constexpr float kBattWarningVolts = 14.4f;
    static constexpr float kBattCriticalVolts = 13.2f;
    static constexpr float kMaxTiltAngleDeg = 75.0f;

    struct ActionFlags {
        bool deploy_parachute{false};
        bool disarm_motors{false};
        bool execute_rth{false};
        bool execute_land{false};
    };

    constexpr FailsafeManager() noexcept = default;

    void update(const VehicleHealth& health, uint32_t now_ms) noexcept {
        const bool rc_lost = (now_ms - health.last_rc_packet_ms) > kRcTimeoutMs;
        const bool gps_lost = (now_ms - health.last_gps_fix_ms) > kGpsTimeoutMs;
        const bool imu_lost = (now_ms - health.last_imu_sample_ms) > kImuTimeoutMs;
        const bool batt_critical = health.battery_voltage_v < kBattCriticalVolts;
        const bool batt_warning = health.battery_voltage_v < kBattWarningVolts;
        const bool angle_exceeded = (health.roll_deg > kMaxTiltAngleDeg) ||
                                    (health.roll_deg < -kMaxTiltAngleDeg) ||
                                    (health.pitch_deg > kMaxTiltAngleDeg) ||
                                    (health.pitch_deg < -kMaxTiltAngleDeg);

        // 1. Аварійне переривання польоту при втраті кутової стабілізації
        if (angle_exceeded || imu_lost) {
            state_ = FailsafeState::CriticalTerminate;
            actions_.deploy_parachute = true;
            actions_.disarm_motors = true;
            return;
        }

        // 2. Ієрархічні переходи
        switch (state_) {
            case FailsafeState::Normal:
                if (rc_lost && !gps_lost) {
                    transition_to(FailsafeState::AutoRth, now_ms);
                } else if (rc_lost && gps_lost) {
                    transition_to(FailsafeState::EmergencyDescent, now_ms);
                } else if (batt_warning || !health.i2c_bus_healthy) {
                    transition_to(FailsafeState::SensorDegraded, now_ms);
                }
                break;

            case FailsafeState::SensorDegraded:
                if (batt_critical) {
                    transition_to(FailsafeState::EmergencyDescent, now_ms);
                } else if (rc_lost && !gps_lost) {
                    transition_to(FailsafeState::AutoRth, now_ms);
                } else if (!rc_lost && !batt_warning && health.i2c_bus_healthy) {
                    transition_to(FailsafeState::Normal, now_ms);
                }
                break;

            case FailsafeState::AutoRth:
                if (batt_critical || gps_lost) {
                    transition_to(FailsafeState::EmergencyDescent, now_ms);
                }
                break;

            case FailsafeState::EmergencyDescent:
                if (now_ms - state_entry_time_ms_ > 30000) {
                    actions_.disarm_motors = true;
                }
                break;

            case FailsafeState::CriticalTerminate:
                actions_.deploy_parachute = true;
                actions_.disarm_motors = true;
                break;
        }

        apply_actions();
    }

    // Апаратне відновлення шини I2C
    static bool clear_i2c_bus(const std::function<void(bool)>& set_scl,
                              const std::function<void(bool)>& set_sda,
                              const std::function<bool()>& read_sda,
                              const std::function<void(uint32_t)>& delay_us) {
        set_sda(true);
        delay_us(5);
        if (read_sda()) return true;

        for (uint8_t i = 0; i < 9; ++i) {
            set_scl(false);
            delay_us(5);
            set_scl(true);
            delay_us(5);
            if (read_sda()) break;
        }

        // STOP condition
        set_sda(false);
        delay_us(5);
        set_scl(true);
        delay_us(5);
        set_sda(true);
        delay_us(5);

        return read_sda();
    }

    [[nodiscard]] FailsafeState get_state() const noexcept { return state_; }
    [[nodiscard]] const ActionFlags& get_actions() const noexcept { return actions_; }

private:
    void transition_to(FailsafeState next, uint32_t now_ms) noexcept {
        state_ = next;
        state_entry_time_ms_ = now_ms;
    }

    void apply_actions() noexcept {
        actions_.execute_rth = (state_ == FailsafeState::AutoRth);
        actions_.execute_land = (state_ == FailsafeState::EmergencyDescent);
    }

    FailsafeState state_{FailsafeState::Normal};
    uint32_t state_entry_time_ms_{0};
    ActionFlags actions_{};
};
