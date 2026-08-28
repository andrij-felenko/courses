// DockingController.hpp
#pragma once

#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <optional>
#include <span>

namespace DroneDock {

struct CameraIntrinsics {
    float fx{800.0F};
    float fy{800.0F};
    float cx{320.0F};
    float cy{240.0F};
    float tagSizeM{0.2F};
};

struct FiducialCorners {
    std::array<float, 4> u{};
    std::array<float, 4> v{};
    uint32_t tagId{0};
    std::chrono::microseconds timestampUs{0};
    bool valid{false};
};

struct TargetState {
    std::array<float, 3> posBody{};
    std::array<float, 3> velBody{};
    float yawRelativeRad{0.0F};
    std::chrono::microseconds timestampUs{0};
    bool isTracking{false};
};

struct GuidanceParams {
    float kpXy{1.2F};
    float kdXy{0.3F};
    float kzDesc{0.5F};
    float maxHorizVel{1.5F};
    float maxDescVel{0.7F};
    float minDescVel{0.15F};
    float landHeightThreshold{0.3F};
};

struct GuidanceCommand {
    std::array<float, 3> velCmdBody{};
    float yawRateCmdRad{0.0F};
    bool initiateTouchdown{false};
    bool abortLanding{false};
};

enum class DockState : uint8_t {
    Idle,
    RoofOpening,
    WaitingUavApproach,
    TouchdownConfirmed,
    MechanicalClamping,
    ContactProbe,
    PrechargeSoftstart,
    MainCharging,
    ChargeComplete,
    EmergencyIsolation
};

struct HardwareInputs {
    float senseVoltageDropMv{0.0F};
    float probeCurrentMa{0.0F};
    float batteryVoltageMv{0.0F};
    float chargeCurrentA{0.0F};
    std::array<float, 6> cellTemperaturesC{};
    uint8_t cellCount{6};
    bool uavDisarmed{false};
    bool bmsCanAlive{false};
    bool emergencyStopPressed{false};
};

struct HardwareOutputs {
    bool roofOpenCmd{false};
    bool clampMotorsEngage{false};
    bool probeGeneratorEnable{false};
    bool prechargeRelayEnable{false};
    bool mainPowerRelayEnable{false};
    bool coolingFansEnable{false};
    float targetPsuVoltageV{0.0F};
    float targetPsuCurrentLimitA{0.0F};
};

class KalmanFilter3D {
public:
    constexpr KalmanFilter3D() noexcept {
        reset();
    }

    void reset() noexcept {
        x_.fill(0.0F);
        for (size_t i = 0; i < 6; ++i) {
            for (size_t j = 0; j < 6; ++j) {
                P_[i][j] = (i == j) ? 1.0F : 0.0F;
            }
        }
        initialized_ = false;
    }

    void predict(float dt) noexcept {
        if (!initialized_ || dt <= 0.0F) return;

        for (size_t i = 0; i < 3; ++i) {
            x_[i] += x_[i + 3] * dt;
        }

        constexpr float qPos = 0.05F;
        constexpr float qVel = 0.1F;

        for (size_t i = 0; i < 3; ++i) {
            P_[i][i] += (P_[i + 3][i + 3] * dt * dt) + (2.0F * P_[i][i + 3] * dt) + (qPos * dt);
            P_[i][i + 3] += P_[i + 3][i + 3] * dt;
            P_[i + 3][i] = P_[i][i + 3];
            P_[i + 3][i + 3] += qVel * dt;
        }
    }

    void update(std::span<const float, 3> measPos) noexcept {
        if (!initialized_) {
            for (size_t i = 0; i < 3; ++i) {
                x_[i] = measPos[i];
                x_[i + 3] = 0.0F;
            }
            initialized_ = true;
            return;
        }

        constexpr float rPos = 0.02F;
        for (size_t i = 0; i < 3; ++i) {
            const float y = measPos[i] - x_[i];
            const float s = P_[i][i] + rPos;
            if (std::abs(s) > 1e-6F) {
                const float kGain = P_[i][i] / s;
                const float kGainVel = P_[i + 3][i] / s;

                x_[i] += kGain * y;
                x_[i + 3] += kGainVel * y;

                P_[i][i] *= (1.0F - kGain);
                P_[i + 3][i + 3] -= kGainVel * P_[i][i + 3];
                P_[i][i + 3] *= (1.0F - kGain);
                P_[i + 3][i] = P_[i][i + 3];
            }
        }
    }

    [[nodiscard]] std::array<float, 3> getPosition() const noexcept {
        return {x_[0], x_[1], x_[2]};
    }

    [[nodiscard]] std::array<float, 3> getVelocity() const noexcept {
        return {x_[3], x_[4], x_[5]};
    }

private:
    std::array<float, 6> x_{};
    std::array<std::array<float, 6>, 6> P_{};
    bool initialized_{false};
};

class PrecisionDockingEstimator {
public:
    explicit constexpr PrecisionDockingEstimator(CameraIntrinsics intrinsics) noexcept
        : intrinsics_{intrinsics} {}

    [[nodiscard]] std::optional<TargetState> processCorners(const FiducialCorners& corners, float dt) noexcept {
        if (!corners.valid) {
            targetState_.isTracking = false;
            return std::nullopt;
        }

        const float du1 = corners.u[1] - corners.u[0];
        const float dv1 = corners.v[1] - corners.v[0];
        const float pixelWidth = std::sqrt(du1 * du1 + dv1 * dv1);

        if (pixelWidth < 4.0F) {
            targetState_.isTracking = false;
            return std::nullopt;
        }

        const float zCam = (intrinsics_.fx * intrinsics_.tagSizeM) / pixelWidth;
        const float uCenter = (corners.u[0] + corners.u[1] + corners.u[2] + corners.u[3]) * 0.25F;
        const float vCenter = (corners.v[0] + corners.v[1] + corners.v[2] + corners.v[3]) * 0.25F;

        const float xCam = (uCenter - intrinsics_.cx) * zCam / intrinsics_.fx;
        const float yCam = (vCenter - intrinsics_.cy) * zCam / intrinsics_.fy;

        const std::array<float, 3> measBody{yCam, xCam, zCam};

        kalman_.predict(dt);
        kalman_.update(measBody);

        targetState_.posBody = kalman_.getPosition();
        targetState_.velBody = kalman_.getVelocity();
        targetState_.yawRelativeRad = std::atan2(dv1, du1);
        targetState_.timestampUs = corners.timestampUs;
        targetState_.isTracking = true;

        return targetState_;
    }

private:
    CameraIntrinsics intrinsics_{};
    KalmanFilter3D kalman_{};
    TargetState targetState_{};
};

class DockStationController {
public:
    constexpr DockStationController() noexcept = default;

    void update(const HardwareInputs& in, HardwareOutputs& out, std::chrono::milliseconds dt) noexcept {
        stateTimer_ += dt;

        if (in.emergencyStopPressed) {
            state_ = DockState::EmergencyIsolation;
        }

        switch (state_) {
        case DockState::Idle:
            out = {};
            break;

        case DockState::RoofOpening:
            out.roofOpenCmd = true;
            if (stateTimer_ > std::chrono::seconds(4)) {
                transitionTo(DockState::WaitingUavApproach);
            }
            break;

        case DockState::WaitingUavApproach:
            out.roofOpenCmd = true;
            if (in.uavDisarmed) {
                transitionTo(DockState::TouchdownConfirmed);
            }
            break;

        case DockState::TouchdownConfirmed:
            if (stateTimer_ > std::chrono::seconds(2)) {
                transitionTo(DockState::MechanicalClamping);
            }
            break;

        case DockState::MechanicalClamping:
            out.clampMotorsEngage = true;
            if (stateTimer_ > std::chrono::milliseconds(3500)) {
                transitionTo(DockState::ContactProbe);
            }
            break;

        case DockState::ContactProbe:
            out.probeGeneratorEnable = true;
            if (in.probeCurrentMa > 50.0F) {
                contactResistanceMohm_ = (in.senseVoltageDropMv / in.probeCurrentMa) * 1000.0F;
                if (contactResistanceMohm_ < 40.0F && in.bmsCanAlive) {
                    transitionTo(DockState::PrechargeSoftstart);
                } else if (stateTimer_ > std::chrono::seconds(2)) {
                    if (retryCount_++ < 3) {
                        transitionTo(DockState::MechanicalClamping);
                    } else {
                        transitionTo(DockState::EmergencyIsolation);
                    }
                }
            }
            break;

        case DockState::PrechargeSoftstart:
            out.probeGeneratorEnable = false;
            out.prechargeRelayEnable = true;
            out.targetPsuVoltageV = 25.2F;
            out.targetPsuCurrentLimitA = 2.0F;

            if (stateTimer_ > std::chrono::milliseconds(150)) {
                transitionTo(DockState::MainCharging);
            }
            break;

        case DockState::MainCharging:
            out.prechargeRelayEnable = true;
            out.mainPowerRelayEnable = true;
            out.coolingFansEnable = true;
            out.targetPsuVoltageV = 25.2F;
            out.targetPsuCurrentLimitA = 15.0F;

            for (size_t i = 0; i < in.cellCount; ++i) {
                if (in.cellTemperaturesC[i] > 48.0F) {
                    transitionTo(DockState::EmergencyIsolation);
                    return;
                }
            }

            if (in.batteryVoltageMv >= 25150.0F && in.chargeCurrentA < 0.5F) {
                if (stateTimer_ > std::chrono::seconds(5)) {
                    transitionTo(DockState::ChargeComplete);
                }
            }
            break;

        case DockState::ChargeComplete:
            out.mainPowerRelayEnable = false;
            out.prechargeRelayEnable = false;
            out.coolingFansEnable = false;
            break;

        case DockState::EmergencyIsolation:
        default:
            out = {};
            break;
        }
    }

    [[nodiscard]] DockState getState() const noexcept { return state_; }
    [[nodiscard]] float getContactResistanceMohm() const noexcept { return contactResistanceMohm_; }

private:
    void transitionTo(DockState nextState) noexcept {
        state_ = nextState;
        stateTimer_ = std::chrono::milliseconds(0);
    }

    DockState state_{DockState::Idle};
    std::chrono::milliseconds stateTimer_{0};
    float contactResistanceMohm_{0.0F};
    uint8_t retryCount_{0};
};

} // namespace DroneDock
