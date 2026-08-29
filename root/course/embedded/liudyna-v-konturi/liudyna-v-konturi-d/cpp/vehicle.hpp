#pragma once

#include "pio.hpp"

namespace hitl {

// Фізика однієї осі: I*theta'' = M_кер + M_збур - b*theta'
class Airframe {
public:
    Airframe(float inertia, float damping, float torque_gain);

    void Step(float control, float disturbance, float dt) noexcept;

    [[nodiscard]] float angle() const noexcept { return angle_rad_; }
    [[nodiscard]] float rate() const noexcept { return rate_rad_s_; }
    [[nodiscard]] float inertia() const noexcept { return inertia_; }
    [[nodiscard]] float damping() const noexcept { return damping_; }
    [[nodiscard]] float torque_gain() const noexcept { return torque_gain_; }

private:
    float inertia_;
    float damping_;
    float torque_gain_;
    float angle_rad_{0.0f};
    float rate_rad_s_{0.0f};
};

enum class ControlMode { Rate, Angle };

// Об'єкт очима оператора — те, під що людина підганяє власні параметри.
struct ObjectDynamics {
    float gain{0.0f};        // стік -> вихід об'єкта (рад/с або рад)
    float lag_tc{0.0f};      // стала часу об'єкта, с
    bool integrating{false}; // стік задає ШВИДКІСТЬ: у контурі вільний інтегратор
};

class Autopilot {
public:
    Autopilot(ControlMode mode, float dt) noexcept;

    void EnableSuppression(bool on) noexcept;
    float Update(float stick, const Airframe& air, float dt) noexcept;

    [[nodiscard]] ObjectDynamics Describe(const Airframe& air) const noexcept;
    [[nodiscard]] float saturation_ratio() const noexcept;
    [[nodiscard]] float sensitivity() const noexcept { return sensitivity_; }

private:
    ControlMode mode_;
    PioMonitor stick_monitor_;
    float kp_angle_{8.0f};       // зовнішній контур кута, 1/с
    float kp_rate_{0.6f};        // внутрішній контур кутової швидкості
    float ki_rate_{1.5f};
    float max_rate_{3.5f};       // ~200 град/с на повному ході стіка
    float max_angle_{0.52f};     // ~30 град
    float torque_limit_{1.5f};   // насичення моторів, Н*м
    float slew_limit_{25.0f};    // максимум d(уставка)/dt, 1/с
    bool suppression_{false};
    float integral_{0.0f};
    float setpoint_{0.0f};
    float sensitivity_{1.0f};
    int steps_{0};
    int saturated_{0};
};

}  // namespace hitl
