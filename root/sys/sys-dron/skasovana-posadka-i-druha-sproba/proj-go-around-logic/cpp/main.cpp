#include <cstdint>
#include <cmath>
#include <algorithm>
#include <optional>

namespace Autopilot::Safety {

inline constexpr float GravityMs2 = 9.80665f;
inline constexpr float DeltaTimeSec = 0.02f; // 50 Hz

enum class GoAroundState : uint8_t {
    ApproachDescent,
    AbortBrakeClimb,
    EnergyAudit,
    CircuitLoiter,
    EmergencyFailsafe
};

struct GoAroundConfig {
    float maxThrustToWeight{1.8f};
    float motorSpoolupTimeSec{0.20f};
    float safetyMarginM{0.8f};
    float missedApproachAltM{25.0f};
    float obstacleDistThreshM{1.5f};
    float maxTiltAngleRad{0.436f};    // ~25 deg
    float minSocForRetry{0.22f};
    float minCellVoltageV{3.35f};
    uint8_t cellCount{6U};
    uint8_t maxAttempts{2U};
    uint32_t loiterDurationMs{15000U};
    uint8_t lidarConfirmTicks{5U};
};

struct TelemetrySnapshot {
    float altitudeM{0.0f};
    float verticalSpeedMs{0.0f};      // Negative during descent
    float lidarDistanceM{0.0f};
    float rollRad{0.0f};
    float pitchRad{0.0f};
    float batteryVoltageV{24.0f};
    float batteryCurrentA{0.0f};
    float batterySoc{1.0f};           // 0.0 .. 1.0
    bool lidarValid{false};
    bool operatorAbortReq{false};
};

struct ControllerSetpoints {
    float targetAltM{0.0f};
    float targetVzMs{-1.0f};
    float targetRollRad{0.0f};
    float targetPitchRad{0.0f};
    float maxTiltLimitRad{0.436f};
    bool climbPriority{false};
    bool emergencyLandNow{false};
};

class GoAroundStateMachine {
public:
    explicit GoAroundStateMachine(const GoAroundConfig& config = GoAroundConfig{}) noexcept
        : m_config(config) {}

    void step(const TelemetrySnapshot& telem, uint32_t nowMs) noexcept {
        switch (m_state) {
        case GoAroundState::ApproachDescent:
            m_setpoints.targetVzMs = -1.0f;
            m_setpoints.climbPriority = false;
            m_setpoints.maxTiltLimitRad = m_config.maxTiltAngleRad;
            m_setpoints.emergencyLandNow = false;

            if (checkAbortConditions(telem)) {
                const float sinkage = calculateSinkage(telem.verticalSpeedMs);

                // Якщо висоти замало для безпечного гальмування — примусова аварійна посадка
                if (telem.altitudeM < (sinkage + m_config.safetyMarginM)) {
                    m_state = GoAroundState::EmergencyFailsafe;
                    m_setpoints.emergencyLandNow = true;
                } else {
                    ++m_attemptCounter;
                    m_state = GoAroundState::AbortBrakeClimb;
                    m_setpoints.targetAltM = telem.altitudeM + m_config.missedApproachAltM;
                    m_stateTimerMs = nowMs;
                }
            }
            break;

        case GoAroundState::AbortBrakeClimb:
            // Екстрений вертикальний набір з фіксацією нахилів
            m_setpoints.targetVzMs = 3.5f;
            m_setpoints.targetRollRad = 0.0f;
            m_setpoints.targetPitchRad = 0.0f;
            m_setpoints.maxTiltLimitRad = 0.087f; // ~5 deg
            m_setpoints.climbPriority = true;

            if (telem.altitudeM >= m_setpoints.targetAltM) {
                m_state = GoAroundState::EnergyAudit;
                m_stateTimerMs = nowMs;
            }
            break;

        case GoAroundState::EnergyAudit:
            m_setpoints.climbPriority = false;
            m_setpoints.targetVzMs = 0.0f; // Зависання
            m_setpoints.maxTiltLimitRad = m_config.maxTiltAngleRad;

            if (isEnergyBudgetSufficient(telem)) {
                m_state = GoAroundState::CircuitLoiter;
            } else {
                m_state = GoAroundState::EmergencyFailsafe;
            }
            m_stateTimerMs = nowMs;
            break;

        case GoAroundState::CircuitLoiter:
            m_setpoints.targetVzMs = 0.0f;
            if (nowMs - m_stateTimerMs >= m_config.loiterDurationMs) {
                m_state = GoAroundState::ApproachDescent;
                m_stateTimerMs = nowMs;
                m_lidarObstacleCounter = 0U;
            }
            break;

        case GoAroundState::EmergencyFailsafe:
            m_setpoints.targetVzMs = -0.6f;
            m_setpoints.climbPriority = false;
            break;
        }
    }

    [[nodiscard]] GoAroundState state() const noexcept { return m_state; }
    [[nodiscard]] uint8_t attempts() const noexcept { return m_attemptCounter; }
    [[nodiscard]] const ControllerSetpoints& setpoints() const noexcept { return m_setpoints; }

    void reset() noexcept {
        m_state = GoAroundState::ApproachDescent;
        m_attemptCounter = 0U;
        m_lidarObstacleCounter = 0U;
        m_stateTimerMs = 0U;
        m_setpoints = ControllerSetpoints{};
    }

private:
    [[nodiscard]] float calculateSinkage(float vz) const noexcept {
        if (vz >= 0.0f) {
            return 0.0f;
        }
        const float absVz = std::abs(vz);
        const float aClimb = std::max(1.0f, (m_config.maxThrustToWeight - 1.0f) * GravityMs2);
        const float hSpool = absVz * m_config.motorSpoolupTimeSec;
        const float hBrake = (absVz * absVz) / (2.0f * aClimb);
        return hSpool + hBrake;
    }

    [[nodiscard]] bool checkAbortConditions(const TelemetrySnapshot& telem) noexcept {
        if (telem.operatorAbortReq) {
            return true;
        }

        if (telem.lidarValid && (telem.lidarDistanceM < m_config.obstacleDistThreshM)) {
            if (m_lidarObstacleCounter < m_config.lidarConfirmTicks) {
                ++m_lidarObstacleCounter;
            }
        } else {
            m_lidarObstacleCounter = 0U;
        }

        if (m_lidarObstacleCounter >= m_config.lidarConfirmTicks) {
            return true;
        }

        return (std::abs(telem.rollRad) > m_config.maxTiltAngleRad) ||
               (std::abs(telem.pitchRad) > m_config.maxTiltAngleRad);
    }

    [[nodiscard]] bool isEnergyBudgetSufficient(const TelemetrySnapshot& telem) const noexcept {
        if (m_attemptCounter >= m_config.maxAttempts) {
            return false;
        }
        if (telem.batterySoc < m_config.minSocForRetry) {
            return false;
        }
        const float cellVoltage = telem.batteryVoltageV / static_cast<float>(m_config.cellCount);
        return cellVoltage >= m_config.minCellVoltageV;
    }

    GoAroundConfig m_config;
    GoAroundState m_state{GoAroundState::ApproachDescent};
    uint8_t m_attemptCounter{0U};
    uint8_t m_lidarObstacleCounter{0U};
    uint32_t m_stateTimerMs{0U};
    ControllerSetpoints m_setpoints{};
};

} // namespace Autopilot::Safety
