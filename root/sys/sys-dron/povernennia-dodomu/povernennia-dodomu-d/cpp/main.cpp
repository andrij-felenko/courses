#include <cstdint>
#include <cmath>
#include <algorithm>
#include <chrono>

enum class RtlState : uint8_t {
    Idle = 0,
    Climb,              // Фаза 1: Вертикальний набір безпечної висоти
    ReturnTransit,      // Фаза 2: Крейсерський рух до бази (Direct/Reverse)
    HoverAlign,         // Фаза 3: Зависання над точкою та пошук мітки
    PrecisionDescent,   // Фаза 4: Оптичне зниження з контролем конуса
    TouchdownWait,      // Фаза 5: Детектування землі та відлік таймауту
    Completed           // Фінал: Мотори зупинено (Disarmed)
};

struct NavPose {
    float x{0.0f};      // Координати в локальній системі NED (метри)
    float y{0.0f};
    float z{0.0f};
    float vx{0.0f};     // Швидкості NED (м/с)
    float vy{0.0f};
    float vz{0.0f};
};

struct OpticalTarget {
    float x{0.0f};      // Зміщення мітки в системі NED відносно дрона
    float y{0.0f};
    float z{0.0f};
    bool  isDetected{false};
};

struct RtlConfig {
    float rtlAltitudeMin{30.0f};
    float cruiseSpeedXy{12.0f};
    float climbRateZ{2.5f};
    float descentRateFast{1.5f};
    float descentRateSlow{0.4f};
    float maxTiltAngleRad{0.61f}; // ~35 градусів
    float homeReachRadius{2.0f};
};

class RtlController {
public:
    using Milliseconds = std::chrono::milliseconds;

    RtlController(const RtlConfig& config, const NavPose& homePose) noexcept
        : config_(config), homePose_(homePose) {}

    void start(const NavPose& currentPose) noexcept {
        targetCruiseAlt_ = std::max(currentPose.z, config_.rtlAltitudeMin);
        state_ = RtlState::Climb;
        groundContactStartMs_ = 0;
        disarmCommanded_ = false;
    }

    void update(const NavPose& cur, const OpticalTarget& opt, float throttleOut,
                uint32_t nowMs, NavPose& cmdOut) noexcept {
        switch (state_) {
            case RtlState::Climb:
                handleClimb(cur, cmdOut);
                break;
            case RtlState::ReturnTransit:
                handleTransit(cur, cmdOut);
                break;
            case RtlState::HoverAlign:
                handleHoverAlign(cur, cmdOut);
                break;
            case RtlState::PrecisionDescent:
                handlePrecisionDescent(cur, opt, throttleOut, nowMs, cmdOut);
                break;
            case RtlState::TouchdownWait:
                handleTouchdownWait(cur, throttleOut, nowMs, cmdOut);
                break;
            case RtlState::Completed:
            case RtlState::Idle:
            default:
                cmdOut.vx = 0.0f;
                cmdOut.vy = 0.0f;
                cmdOut.vz = 0.0f;
                break;
        }
    }

    [[nodiscard]] RtlState state() const noexcept { return state_; }
    [[nodiscard]] bool isDisarmCommanded() const noexcept { return disarmCommanded_; }

private:
    void handleClimb(const NavPose& cur, NavPose& cmdOut) noexcept {
        cmdOut.x = cur.x;
        cmdOut.y = cur.y;
        cmdOut.z = targetCruiseAlt_;
        cmdOut.vz = config_.climbRateZ;
        cmdOut.vx = 0.0f;
        cmdOut.vy = 0.0f;

        if (cur.z >= (targetCruiseAlt_ - 0.5f)) {
            state_ = RtlState::ReturnTransit;
        }
    }

    void handleTransit(const NavPose& cur, NavPose& cmdOut) noexcept {
        const float dx = homePose_.x - cur.x;
        const float dy = homePose_.y - cur.y;
        const float dist = std::hypot(dx, dy);

        cmdOut.x = homePose_.x;
        cmdOut.y = homePose_.y;
        cmdOut.z = targetCruiseAlt_;
        cmdOut.vz = 0.0f;

        if (dist > config_.homeReachRadius) {
            cmdOut.vx = (dx / dist) * config_.cruiseSpeedXy;
            cmdOut.vy = (dy / dist) * config_.cruiseSpeedXy;
        } else {
            cmdOut.vx = 0.0f;
            cmdOut.vy = 0.0f;
            state_ = RtlState::HoverAlign;
        }
    }

    void handleHoverAlign(const NavPose& /*cur*/, NavPose& cmdOut) noexcept {
        cmdOut.x = homePose_.x;
        cmdOut.y = homePose_.y;
        cmdOut.z = targetCruiseAlt_;
        cmdOut.vx = 0.0f;
        cmdOut.vy = 0.0f;
        cmdOut.vz = 0.0f;

        state_ = RtlState::PrecisionDescent;
    }

    void handlePrecisionDescent(const NavPose& cur, const OpticalTarget& opt,
                                float throttleOut, uint32_t nowMs, NavPose& cmdOut) noexcept {
        float vzTarget = (cur.z > 5.0f) ? -config_.descentRateFast : -config_.descentRateSlow;

        if (opt.isDetected) {
            constexpr float kpOpt = 0.8f;
            cmdOut.vx = -kpOpt * opt.x;
            cmdOut.vy = -kpOpt * opt.y;

            const float optOffset = std::hypot(opt.x, opt.y);
            if (optOffset > (cur.z * 0.3f) && cur.z > 1.5f) {
                vzTarget = 0.0f; // Призупинити зниження, доки не сцентруємось
            }
        } else {
            cmdOut.x = homePose_.x;
            cmdOut.y = homePose_.y;
            cmdOut.vx = 0.0f;
            cmdOut.vy = 0.0f;
        }

        cmdOut.z = 0.0f;
        cmdOut.vz = vzTarget;

        if (cur.z < 1.0f && std::abs(cur.vz) < 0.15f && throttleOut < 0.25f) {
            state_ = RtlState::TouchdownWait;
            groundContactStartMs_ = nowMs;
        }
    }

    void handleTouchdownWait(const NavPose& cur, float throttleOut,
                             uint32_t nowMs, NavPose& cmdOut) noexcept {
        cmdOut.vx = 0.0f;
        cmdOut.vy = 0.0f;
        cmdOut.vz = -0.2f;

        if (std::abs(cur.vz) < 0.15f && throttleOut < 0.25f) {
            if ((nowMs - groundContactStartMs_) > 1200u) {
                disarmCommanded_ = true;
                state_ = RtlState::Completed;
            }
        } else {
            state_ = RtlState::PrecisionDescent;
        }
    }

    RtlConfig     config_;
    NavPose       homePose_;
    RtlState      state_{RtlState::Idle};
    float         targetCruiseAlt_{30.0f};
    uint32_t      groundContactStartMs_{0};
    bool          disarmCommanded_{false};
};
