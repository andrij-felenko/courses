#include <cstdint>
#include <cmath>
#include <array>
#include <algorithm>

struct Point3D {
    float x{0.0f};      // Координати NED (м)
    float y{0.0f};
    float z{0.0f};
    float vx{0.0f};     // Швидкості NED (м/с)
    float vy{0.0f};
    float vz{0.0f};
};

struct VisionTarget {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
    bool  valid{false};
};

struct RtlParameters {
    float minRtlAltM{30.0f};
    float cruiseSpeedMs{12.0f};
    float climbSpeedMs{2.5f};
    float descentFastMs{1.5f};
    float descentSlowMs{0.4f};
    float acceptRadiusM{2.0f};
    float opticalKp{0.8f};
};

enum class FsmState : uint8_t {
    Idle = 0,
    ClimbSafeAlt,
    ReversePathTransit,
    DirectHomeTransit,
    HoverSearchTarget,
    PrecisionDescent,
    GroundWaitDisarm,
    DisarmedDone
};

template <std::size_t Capacity = 64>
class BreadcrumbBuffer {
public:
    void push(const Point3D& p, float minDistance = 8.0f) noexcept {
        if (count_ > 0) {
            const auto lastIdx = (head_ == 0) ? (Capacity - 1) : (head_ - 1);
            const float dx = p.x - buffer_[lastIdx].x;
            const float dy = p.y - buffer_[lastIdx].y;
            const float dz = p.z - buffer_[lastIdx].z;
            if ((dx * dx + dy * dy + dz * dz) < (minDistance * minDistance)) {
                return;
            }
        }
        buffer_[head_] = p;
        head_ = (head_ + 1) % Capacity;
        if (count_ < Capacity) {
            ++count_;
        }
    }

    [[nodiscard]] std::size_t count() const noexcept { return count_; }
    [[nodiscard]] const Point3D& at(std::size_t index) const noexcept { return buffer_[index]; }
    void clear() noexcept { head_ = 0; count_ = 0; }

private:
    std::array<Point3D, Capacity> buffer_{};
    std::size_t head_{0};
    std::size_t count_{0};
};

class RtlStateMachine {
public:
    RtlStateMachine(const RtlParameters& params, const Point3D& homePoint) noexcept
        : params_(params), homePoint_(homePoint) {}

    void recordBreadcrumb(const Point3D& current) noexcept {
        crumbs_.push(current);
    }

    void trigger(const Point3D& current) noexcept {
        const float curAlt = -current.z;
        activeCruiseAltM_ = std::max(curAlt, params_.minRtlAltM);
        crumbReverseIdx_ = static_cast<int32_t>(crumbs_.count()) - 1;
        state_ = FsmState::ClimbSafeAlt;
        groundTimerStartMs_ = 0;
        disarmSignal_ = false;
    }

    void step(const Point3D& cur, const VisionTarget& vision, float throttleRatio,
              uint32_t nowMs, Point3D& cmdOut) noexcept {
        switch (state_) {
            case FsmState::ClimbSafeAlt:
                handleClimb(cur, cmdOut);
                break;
            case FsmState::ReversePathTransit:
                handleReverseTransit(cur, cmdOut);
                break;
            case FsmState::DirectHomeTransit:
                handleDirectTransit(cur, cmdOut);
                break;
            case FsmState::HoverSearchTarget:
                handleHoverSearch(cur, cmdOut);
                break;
            case FsmState::PrecisionDescent:
                handlePrecisionDescent(cur, vision, throttleRatio, nowMs, cmdOut);
                break;
            case FsmState::GroundWaitDisarm:
                handleGroundWait(cur, throttleRatio, nowMs, cmdOut);
                break;
            case FsmState::DisarmedDone:
            case FsmState::Idle:
            default:
                cmdOut.vx = 0.0f;
                cmdOut.vy = 0.0f;
                cmdOut.vz = 0.0f;
                break;
        }
    }

    [[nodiscard]] FsmState state() const noexcept { return state_; }
    [[nodiscard]] bool isDisarmSignaled() const noexcept { return disarmSignal_; }

private:
    void handleClimb(const Point3D& cur, Point3D& cmdOut) noexcept {
        cmdOut.x = cur.x;
        cmdOut.y = cur.y;
        cmdOut.z = -activeCruiseAltM_;
        cmdOut.vz = -params_.climbSpeedMs;
        cmdOut.vx = 0.0f;
        cmdOut.vy = 0.0f;

        if ((-cur.z) >= (activeCruiseAltM_ - 0.5f)) {
            state_ = (crumbReverseIdx_ >= 0) ? FsmState::ReversePathTransit 
                                             : FsmState::DirectHomeTransit;
        }
    }

    void handleReverseTransit(const Point3D& cur, Point3D& cmdOut) noexcept {
        if (crumbReverseIdx_ < 0) {
            state_ = FsmState::DirectHomeTransit;
            return;
        }

        const auto& target = crumbs_.at(static_cast<std::size_t>(crumbReverseIdx_));
        const float dx = target.x - cur.x;
        const float dy = target.y - cur.y;
        const float dist = std::hypot(dx, dy);

        cmdOut.x = target.x;
        cmdOut.y = target.y;
        cmdOut.z = -activeCruiseAltM_;
        cmdOut.vz = 0.0f;

        if (dist > params_.acceptRadiusM) {
            cmdOut.vx = (dx / dist) * params_.cruiseSpeedMs;
            cmdOut.vy = (dy / dist) * params_.cruiseSpeedMs;
        } else {
            --crumbReverseIdx_;
            if (crumbReverseIdx_ < 0) {
                state_ = FsmState::DirectHomeTransit;
            }
        }
    }

    void handleDirectTransit(const Point3D& cur, Point3D& cmdOut) noexcept {
        const float dx = homePoint_.x - cur.x;
        const float dy = homePoint_.y - cur.y;
        const float dist = std::hypot(dx, dy);

        cmdOut.x = homePoint_.x;
        cmdOut.y = homePoint_.y;
        cmdOut.z = -activeCruiseAltM_;
        cmdOut.vz = 0.0f;

        if (dist > params_.acceptRadiusM) {
            cmdOut.vx = (dx / dist) * params_.cruiseSpeedMs;
            cmdOut.vy = (dy / dist) * params_.cruiseSpeedMs;
        } else {
            cmdOut.vx = 0.0f;
            cmdOut.vy = 0.0f;
            state_ = FsmState::HoverSearchTarget;
        }
    }

    void handleHoverSearch(const Point3D& /*cur*/, Point3D& cmdOut) noexcept {
        cmdOut.x = homePoint_.x;
        cmdOut.y = homePoint_.y;
        cmdOut.z = -activeCruiseAltM_;
        cmdOut.vx = 0.0f;
        cmdOut.vy = 0.0f;
        cmdOut.vz = 0.0f;
        state_ = FsmState::PrecisionDescent;
    }

    void handlePrecisionDescent(const Point3D& cur, const VisionTarget& vision,
                                float throttleRatio, uint32_t nowMs, Point3D& cmdOut) noexcept {
        const float curAlt = -cur.z;
        float vzDesc = (curAlt > 5.0f) ? params_.descentFastMs : params_.descentSlowMs;

        if (vision.valid) {
            cmdOut.vx = -params_.opticalKp * vision.x;
            cmdOut.vy = -params_.opticalKp * vision.y;

            const float offset = std::hypot(vision.x, vision.y);
            if (offset > (curAlt * 0.35f) && curAlt > 1.2f) {
                vzDesc = 0.0f;
            }
        } else {
            cmdOut.x = homePoint_.x;
            cmdOut.y = homePoint_.y;
            cmdOut.vx = 0.0f;
            cmdOut.vy = 0.0f;
        }

        cmdOut.z = 0.0f;
        cmdOut.vz = vzDesc;

        if (curAlt < 0.8f && std::abs(cur.vz) < 0.12f && throttleRatio < 0.20f) {
            state_ = FsmState::GroundWaitDisarm;
            groundTimerStartMs_ = nowMs;
        }
    }

    void handleGroundWait(const Point3D& cur, float throttleRatio,
                          uint32_t nowMs, Point3D& cmdOut) noexcept {
        cmdOut.vx = 0.0f;
        cmdOut.vy = 0.0f;
        cmdOut.vz = 0.15f;

        if (std::abs(cur.vz) < 0.12f && throttleRatio < 0.20f) {
            if ((nowMs - groundTimerStartMs_) >= 1200u) {
                disarmSignal_ = true;
                state_ = FsmState::DisarmedDone;
            }
        } else {
            state_ = FsmState::PrecisionDescent;
        }
    }

    RtlParameters           params_;
    Point3D                 homePoint_;
    BreadcrumbBuffer<64>    crumbs_{};
    FsmState                state_{FsmState::Idle};
    float                   activeCruiseAltM_{30.0f};
    int32_t                 crumbReverseIdx_{-1};
    uint32_t                groundTimerStartMs_{0};
    bool                    disarmSignal_{false};
};
