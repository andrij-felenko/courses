#include <algorithm>

class CascadeController {
public:
    struct Config {
        float kp_pos{10.0f};
        float kp_vel{0.1f};
        float ki_vel{0.01f};
        float max_vel{100.0f};      // rad/s
        float max_current{20.0f};   // Amperes
    };

    explicit CascadeController(const Config& cfg) : cfg_(cfg) {}

    float update(float target_pos, float current_pos, float current_vel, float dt) {
        // 1. Контур позиції (P)
        const float pos_error = target_pos - current_pos;
        const float target_vel = std::clamp(pos_error * cfg_.kp_pos, -cfg_.max_vel, cfg_.max_vel);

        // 2. Контур швидкості (PI з Anti-windup)
        const float vel_error = target_vel - current_vel;
        vel_integrator_ += vel_error * cfg_.ki_vel * dt;
        vel_integrator_ = std::clamp(vel_integrator_, -cfg_.max_current, cfg_.max_current);

        const float i_q_target = vel_error * cfg_.kp_vel + vel_integrator_;
        return std::clamp(i_q_target, -cfg_.max_current, cfg_.max_current);
    }

    void reset() { vel_integrator_ = 0.0f; }

private:
    Config cfg_;
    float vel_integrator_{0.0f};
};
