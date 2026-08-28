#include <cstdint>
#include <cmath>
#include <algorithm>
#include <optional>

namespace FlightSafety {

enum class GoAroundState : uint8_t {
    ApproachDescent,
    AbortBrakeClimb,
    EnergyAudit,
    CircuitLoiter,
    EmergencyFailsafe
};

struct FlightTelemetry {
    float current_alt_m{0.0f};
    float vertical_speed_ms{0.0f};
    float lidar_distance_m{0.0f};
    float roll_rad{0.0f};
    float pitch_rad{0.0f};
    float battery_soc_norm{1.0f};       // 0.0 .. 1.0
    float battery_voltage_v{25.2f};
    bool operator_abort_command{false};
    bool lidar_valid{false};
};

struct FlightSetpoints {
    float target_alt_m{0.0f};
    float target_vz_ms{-1.0f};
    float target_roll_rad{0.0f};
    float target_pitch_rad{0.0f};
    bool climb_priority_active{false};
};

class GoAroundController {
public:
    static constexpr uint8_t MaxAbortAttempts = 2;
    static constexpr float LidarObstacleThresholdM = 1.5f;
    static constexpr float AttitudeMaxTiltRad = 0.436f; // ~25 deg
    static constexpr float MissedApproachAltM = 25.0f;
    static constexpr float ClimbVelocitySetpointMs = 3.0f;
    static constexpr float MinBatterySocForRetry = 0.20f;
    static constexpr float MinBatteryVoltageForRetry = 21.0f; // 6S LiPo cut-off

    constexpr GoAroundController() noexcept = default;

    [[nodiscard]] GoAroundState currentState() const noexcept { return m_state; }
    [[nodiscard]] uint8_t abortCount() const noexcept { return m_abortCounter; }
    [[nodiscard]] const FlightSetpoints& setpoints() const noexcept { return m_setpoints; }

    void update(const FlightTelemetry& telem, uint32_t now_ms) noexcept {
        switch (m_state) {
        case GoAroundState::ApproachDescent:
            m_setpoints.target_vz_ms = -1.0f;
            m_setpoints.climb_priority_active = false;

            if (isAbortTriggered(telem)) {
                ++m_abortCounter;
                m_state = GoAroundState::AbortBrakeClimb;
                m_stateEntryTimeMs = now_ms;
                m_setpoints.target_alt_m = telem.current_alt_m + MissedApproachAltM;
            }
            break;

        case GoAroundState::AbortBrakeClimb:
            // Екстрений вертикальний набір: крен і тангаж затиснуті в 0
            m_setpoints.target_vz_ms = ClimbVelocitySetpointMs;
            m_setpoints.target_roll_rad = 0.0f;
            m_setpoints.target_pitch_rad = 0.0f;
            m_setpoints.climb_priority_active = true;

            if (telem.current_alt_m >= m_setpoints.target_alt_m) {
                m_state = GoAroundState::EnergyAudit;
                m_stateEntryTimeMs = now_ms;
            }
            break;

        case GoAroundState::EnergyAudit:
            m_setpoints.climb_priority_active = false;
            m_setpoints.target_vz_ms = 0.0f; // Зависання

            if ((m_abortCounter >= MaxAbortAttempts) ||
                (telem.battery_soc_norm < MinBatterySocForRetry) ||
                (telem.battery_voltage_v < MinBatteryVoltageForRetry)) {
                m_state = GoAroundState::EmergencyFailsafe;
            } else {
                m_state = GoAroundState::CircuitLoiter;
            }
            m_stateEntryTimeMs = now_ms;
            break;

        case GoAroundState::CircuitLoiter:
            m_setpoints.target_vz_ms = 0.0f;
            if (now_ms - m_stateEntryTimeMs > LoiterHoldTimeMs) {
                m_state = GoAroundState::ApproachDescent;
                m_stateEntryTimeMs = now_ms;
            }
            break;

        case GoAroundState::EmergencyFailsafe:
            m_setpoints.target_vz_ms = -0.6f;
            m_setpoints.climb_priority_active = false;
            break;
        }
    }

private:
    static constexpr uint32_t LoiterHoldTimeMs = 10000U;

    [[nodiscard]] static bool isAbortTriggered(const FlightTelemetry& telem) noexcept {
        if (telem.operator_abort_command) {
            return true;
        }
        if (telem.lidar_valid && (telem.lidar_distance_m < LidarObstacleThresholdM)) {
            return true;
        }
        return (std::abs(telem.roll_rad) > AttitudeMaxTiltRad) ||
               (std::abs(telem.pitch_rad) > AttitudeMaxTiltRad);
    }

    GoAroundState m_state{GoAroundState::ApproachDescent};
    uint8_t m_abortCounter{0};
    uint32_t m_stateEntryTimeMs{0};
    FlightSetpoints m_setpoints{};
};

} // namespace FlightSafety
