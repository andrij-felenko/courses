// ============================================================================
// TakeoffFSM.hpp
// Автомат процедури зльоту безпілотного апарата (C++20)
// ============================================================================
#pragma once

#include <array>
#include <cmath>
#include <span>
#include <string_view>
#include <algorithm>
#include <numeric>

namespace drone::flight {

constexpr size_t MaxMotors = 8;
constexpr float GravityMss = 9.80665f;

enum class TakeoffState : uint8_t {
    Disarmed = 0,
    Spoolup,
    GroundRamp,
    RapidClimb,
    LevelOff,
    Complete,
    Abort
};

enum class AbortReason : uint8_t {
    None = 0,
    TiltExceeded,
    MotorCurrentImbalance,
    MotorRpmLoss,
    SpoolupTimeout,
    TakeoffStuck,
    EkfDivergence,
    ManualCommand
};

struct Telemetry {
    float rollDeg{0.0f};
    float pitchDeg{0.0f};
    float yawDeg{0.0f};
    float altRelM{0.0f};
    float vzMs{0.0f};
    float accelZMss{0.0f};

    bool ekfHealthy{false};
    float ekfHposVariance{0.0f};
    float ekfVposVariance{0.0f};
    uint8_t gnssSats{0};
    float gnssHdop{99.0f};

    float batteryVoltage{0.0f};
    float cellMinVoltage{0.0f};

    uint8_t numMotors{4};
    std::array<float, MaxMotors> motorCurrents{};
    std::array<float, MaxMotors> motorRpm{};
};

struct Config {
    float targetAltM{5.0f};
    float groundClearAltM{1.2f};
    float climbRateMs{2.0f};
    float hoverThrottle{0.50f};
    float idleThrottle{0.08f};
    float maxTiltOnGround{15.0f};
    float maxCurrentImbalance{3.5f};
    float spoolupTimeS{1.0f};
    float liftoffDetectVzMs{0.25f};
};

struct ControlOutput {
    float throttleCmd{0.0f};
    float vzSetpointMs{0.0f};
    float altSetpointM{0.0f};
    bool freezeIntegrators{true};
    bool armCommand{false};
    bool homePointLatchReq{false};
};

class TakeoffFSM {
public:
    explicit constexpr TakeoffFSM(const Config& cfg = Config{}) : config_{cfg} {}

    [[nodiscard]] bool checkPrearm(const Telemetry& telem) const noexcept {
        if (!telem.ekfHealthy) return false;
        if (telem.ekfHposVariance > 1.2f || telem.ekfVposVariance > 2.0f) return false;
        if (telem.gnssSats < 8 || telem.gnssHdop > 1.4f) return false;
        if (std::abs(telem.rollDeg) > 10.0f || std::abs(telem.pitchDeg) > 10.0f) return false;
        if (telem.cellMinVoltage < 3.75f) return false;
        return true;
    }

    bool start(const Telemetry& telem) noexcept {
        if (state_ != TakeoffState::Disarmed) return false;
        if (!checkPrearm(telem)) return false;

        state_ = TakeoffState::Spoolup;
        abortReason_ = AbortReason::None;
        stateTimerS_ = 0.0f;
        liftoffConfirmed_ = false;
        homeLatched_ = false;
        return true;
    }

    void abort(AbortReason reason) noexcept {
        state_ = TakeoffState::Abort;
        abortReason_ = reason;
        stateTimerS_ = 0.0f;
    }

    void update(const Telemetry& telem, float dt, ControlOutput& out) noexcept {
        stateTimerS_ += dt;

        out.throttleCmd = 0.0f;
        out.vzSetpointMs = 0.0f;
        out.altSetpointM = 0.0f;
        out.freezeIntegrators = true;
        out.armCommand = false;
        out.homePointLatchReq = false;

        // Захист від нахилу на землі
        const float tilt = std::hypot(telem.rollDeg, telem.pitchDeg);
        if (state_ >= TakeoffState::Spoolup && state_ <= TakeoffState::GroundRamp) {
            if (tilt > config_.maxTiltOnGround) {
                abort(AbortReason::TiltExceeded);
            }
        }

        switch (state_) {
        case TakeoffState::Disarmed:
            out.armCommand = false;
            out.freezeIntegrators = true;
            break;

        case TakeoffState::Spoolup: {
            out.armCommand = true;
            out.freezeIntegrators = true;

            const float progress = std::clamp(stateTimerS_ / config_.spoolupTimeS, 0.0f, 1.0f);
            out.throttleCmd = config_.idleThrottle * progress;

            if (stateTimerS_ >= config_.spoolupTimeS) {
                if (!checkCurrentSymmetry(telem)) {
                    abort(AbortReason::MotorCurrentImbalance);
                } else {
                    state_ = TakeoffState::GroundRamp;
                    stateTimerS_ = 0.0f;
                }
            }
            break;
        }

        case TakeoffState::GroundRamp: {
            out.armCommand = true;
            out.freezeIntegrators = true;

            const float targetThr = config_.hoverThrottle * 1.25f;
            const float ramp = std::clamp(stateTimerS_ / 0.5f, 0.0f, 1.0f);
            out.throttleCmd = config_.idleThrottle + (targetThr - config_.idleThrottle) * ramp;

            if (telem.vzMs > config_.liftoffDetectVzMs || telem.altRelM > 0.15f) {
                liftoffConfirmed_ = true;
                if (!homeLatched_) {
                    out.homePointLatchReq = true;
                    homeLatched_ = true;
                }
                state_ = TakeoffState::RapidClimb;
                stateTimerS_ = 0.0f;
            } else if (stateTimerS_ > 1.5f) {
                abort(AbortReason::TakeoffStuck);
            }
            break;
        }

        case TakeoffState::RapidClimb:
            out.armCommand = true;
            out.freezeIntegrators = false; // Розморожуємо PID після відриву
            out.vzSetpointMs = config_.climbRateMs;
            out.throttleCmd = config_.hoverThrottle * 1.20f;

            if (telem.altRelM >= config_.groundClearAltM) {
                state_ = TakeoffState::LevelOff;
                stateTimerS_ = 0.0f;
            }
            break;

        case TakeoffState::LevelOff: {
            out.armCommand = true;
            out.freezeIntegrators = false;
            out.altSetpointM = config_.targetAltM;

            const float remaining = config_.targetAltM - telem.altRelM;
            if (remaining < 0.8f) {
                out.vzSetpointMs = std::max(0.2f, config_.climbRateMs * (remaining / 0.8f));
            } else {
                out.vzSetpointMs = config_.climbRateMs;
            }

            if (telem.altRelM >= (config_.targetAltM * 0.95f) && std::abs(telem.vzMs) < 0.3f) {
                state_ = TakeoffState::Complete;
                stateTimerS_ = 0.0f;
            }
            break;
        }

        case TakeoffState::Complete:
            out.armCommand = true;
            out.freezeIntegrators = false;
            out.altSetpointM = config_.targetAltM;
            out.vzSetpointMs = 0.0f;
            out.throttleCmd = config_.hoverThrottle;
            break;

        case TakeoffState::Abort:
        default:
            out.armCommand = false;
            out.throttleCmd = 0.0f;
            out.vzSetpointMs = 0.0f;
            out.freezeIntegrators = true;
            break;
        }
    }

    [[nodiscard]] TakeoffState state() const noexcept { return state_; }
    [[nodiscard]] AbortReason abortReason() const noexcept { return abortReason_; }
    [[nodiscard]] bool isComplete() const noexcept { return state_ == TakeoffState::Complete; }

    [[nodiscard]] std::string_view stateName() const noexcept {
        switch (state_) {
        case TakeoffState::Disarmed:   return "DISARMED";
        case TakeoffState::Spoolup:    return "SPOOLUP";
        case TakeoffState::GroundRamp: return "GROUND_RAMP";
        case TakeoffState::RapidClimb: return "RAPID_CLIMB";
        case TakeoffState::LevelOff:   return "LEVEL_OFF";
        case TakeoffState::Complete:   return "COMPLETE";
        case TakeoffState::Abort:      return "ABORT";
        default:                       return "UNKNOWN";
        }
    }

private:
    [[nodiscard]] bool checkCurrentSymmetry(const Telemetry& telem) const noexcept {
        if (telem.numMotors < 2) return true;
        const auto activeCurrents = std::span(telem.motorCurrents.data(), telem.numMotors);
        const float sum = std::accumulate(activeCurrents.begin(), activeCurrents.end(), 0.0f);
        const float avg = sum / static_cast<float>(telem.numMotors);

        for (float curr : activeCurrents) {
            if (std::abs(curr - avg) > config_.maxCurrentImbalance) {
                return false;
            }
        }
        return true;
    }

    Config config_;
    TakeoffState state_{TakeoffState::Disarmed};
    AbortReason abortReason_{AbortReason::None};
    float stateTimerS_{0.0f};
    bool liftoffConfirmed_{false};
    bool homeLatched_{false};
};

} // namespace drone::flight
