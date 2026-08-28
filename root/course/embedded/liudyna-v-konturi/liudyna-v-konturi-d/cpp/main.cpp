#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <span>
#include <memory>

namespace control {

inline constexpr float kPi = 3.14159265358979323846f;
inline constexpr float kRadToDeg = 180.0f / kPi;

// Кільцевий буфер чистої часової затримки
class TransportDelayQueue {
public:
    TransportDelayQueue(float delay_sec, float dt)
        : delay_samples_(std::max(1, static_cast<int>(delay_sec / dt)))
        , buffer_(delay_samples_ + 1, 0.0f)
        , head_(0) {}

    float PushPop(float in_val) noexcept {
        buffer_[head_] = in_val;
        int read_idx = head_ - delay_samples_;
        if (read_idx < 0) {
            read_idx += static_cast<int>(buffer_.size());
        }
        head_ = (head_ + 1) % buffer_.size();
        return buffer_[read_idx];
    }

private:
    int delay_samples_;
    std::vector<float> buffer_;
    size_t head_;
};

// Модель оператора Макруера
class OperatorModel {
public:
    OperatorModel(float kp, float time_neuromuscular, float time_lead)
        : kp_(kp)
        , tn_(time_neuromuscular)
        , tl_(time_lead)
        , neuromuscular_state_(0.0f)
        , prev_error_(0.0f) {}

    float Update(float error, float dt) noexcept {
        const float error_deriv = (error - prev_error_) / dt;
        prev_error_ = error;

        const float desired_cmd = kp_ * (error + tl_ * error_deriv);
        const float alpha = dt / (tn_ + dt);
        neuromuscular_state_ += alpha * (desired_cmd - neuromuscular_state_);

        return std::clamp(neuromuscular_state_, -1.0f, 1.0f);
    }

    void SetGain(float kp) noexcept { kp_ = kp; }

private:
    float kp_;
    float tn_;
    float tl_;
    float neuromuscular_state_;
    float prev_error_;
};

// Динаміка нахилу апарата
class VehiclePlant {
public:
    VehiclePlant(float inertia, float damping, float torque_gain)
        : inertia_(inertia)
        , damping_(damping)
        , torque_gain_(torque_gain)
        , angle_rad_(0.0f)
        , rate_rad_s_(0.0f) {}

    void Step(float control_torque, float disturbance, float dt) noexcept {
        const float total_torque = (control_torque * torque_gain_) + disturbance - (damping_ * rate_rad_s_);
        const float angular_accel = total_torque / inertia_;

        rate_rad_s_ += angular_accel * dt;
        angle_rad_ += rate_rad_s_ * dt;
    }

    [[nodiscard]] float angle() const noexcept { return angle_rad_; }
    [[nodiscard]] float rate() const noexcept { return rate_rad_s_; }

private:
    float inertia_;
    float damping_;
    float torque_gain_;
    float angle_rad_;
    float rate_rad_s_;
};

enum class ControlMode {
    Rate,
    Angle
};

class FlightController {
public:
    FlightController(ControlMode mode, float kp_angle, float kp_rate)
        : mode_(mode)
        , kp_angle_(kp_angle)
        , kp_rate_(kp_rate) {}

    [[nodiscard]] float Compute(float stick_input, float current_angle, float current_rate) const noexcept {
        if (mode_ == ControlMode::Rate) {
            const float target_rate = stick_input * 3.5f;
            return kp_rate_ * (target_rate - current_rate);
        } else {
            const float target_angle = stick_input * 0.52f;
            const float target_rate = kp_angle_ * (target_angle - current_angle);
            return kp_rate_ * (target_rate - current_rate);
        }
    }

    void SetMode(ControlMode mode) noexcept { mode_ = mode; }

private:
    ControlMode mode_;
    float kp_angle_;
    float kp_rate_;
};

// Замкнений симулятор
class ClosedLoopSimulation {
public:
    ClosedLoopSimulation(float delay_sec, ControlMode mode)
        : dt_(0.002f)
        , video_link_(delay_sec * 0.7f, dt_)
        , rc_link_(delay_sec * 0.3f, dt_)
        , operator_(2.5f, 0.10f, 0.15f)
        , vehicle_(0.02f, 0.05f, 1.2f)
        , fc_(mode, 6.0f, 0.4f) {}

    void Run(float duration_sec) {
        const int steps = static_cast<int>(duration_sec / dt_);
        float max_angle = 0.0f;

        for (int i = 0; i < steps; ++i) {
            const float t = i * dt_;
            const float disturbance = (t >= 0.5f && t <= 0.6f) ? 0.8f : 0.0f;

            const float delayed_angle = video_link_.PushPop(vehicle_.angle());
            const float error = 0.0f - delayed_angle;
            const float stick_cmd = operator_.Update(error, dt_);

            const float delayed_stick = rc_link_.PushPop(stick_cmd);
            const float torque = fc_.Compute(delayed_stick, vehicle_.angle(), vehicle_.rate());

            vehicle_.Step(torque, disturbance, dt_);
            max_angle = std::max(max_angle, std::abs(vehicle_.angle()));

            if (i % 250 == 0) {
                std::cout << "  Час " << t << " c | Кут: "
                          << vehicle_.angle() * kRadToDeg << " град | Стік: "
                          << stick_cmd << "\n";
            }
        }

        if (max_angle > 1.2f) {
            std::cout << "  -> РЕЗУЛЬТАТ: ВИНИКЛА РОЗКАЧКА PIO! Макс кут: "
                      << max_angle * kRadToDeg << " град.\n\n";
        } else {
            std::cout << "  -> РЕЗУЛЬТАТ: Контур стійкий. Похибка скомпенсована.\n\n";
        }
    }

private:
    float dt_;
    TransportDelayQueue video_link_;
    TransportDelayQueue rc_link_;
    OperatorModel operator_;
    VehiclePlant vehicle_;
    FlightController fc_;
};

} // namespace control

int main() {
    std::cout << "=== C++20 Моделювання динаміки контуру «людина-машина» ===\n\n";

    std::cout << "1. Тест: Затримка 50 мс, режим RATE:\n";
    control::ClosedLoopSimulation sim_fast(0.050f, control::ControlMode::Rate);
    sim_fast.Run(5.0f);

    std::cout << "2. Тест: Затримка 250 мс, режим RATE (розкачка):\n";
    control::ClosedLoopSimulation sim_slow_rate(0.250f, control::ControlMode::Rate);
    sim_slow_rate.Run(5.0f);

    std::cout << "3. Тест: Затримка 250 мс, режим ANGLE (компенсація через бортовий контур):\n";
    control::ClosedLoopSimulation sim_slow_angle(0.250f, control::ControlMode::Angle);
    sim_slow_angle.Run(5.0f);

    return 0;
}
