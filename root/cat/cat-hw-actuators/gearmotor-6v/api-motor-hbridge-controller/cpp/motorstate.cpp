#include <cstdint>
#include <algorithm>
#include <cmath>

enum class MotorState {
    Idle = 0,
    Running,
    DeadTime,
    Fault
};

struct MotorTimingConfig {
    uint16_t dead_time_us{5};      // Пауза dead-time у мікросекундах
    int16_t  slew_rate_pct_s{200}; // Максимальний темп наростання (% за секунду)
    int16_t  deadband_pct{10};     // Зона нечутливості редуктора (%)
};

class MotorController {
public:
    explicit MotorController(const MotorTimingConfig& cfg)
        : config_(cfg), state_(MotorState::Idle), target_speed_(0.0f),
          current_speed_(0.0f), dead_time_start_us_(0), last_update_ms_(0), active_dir_(0) {}

    void init() {
        last_update_ms_ = hal_get_time_ms();
        hal_hbridge_disable_all();
    }

    void setSpeed(float speed_pct) {
        if (state_ == MotorState::Fault) {
            return;
        }
        target_speed_ = std::clamp(speed_pct, -100.0f, 100.0f);
    }

    void update() {
        if (state_ == MotorState::Fault) {
            hal_hbridge_disable_all();
            return;
        }

        uint32_t now_ms = hal_get_time_ms();
        uint32_t dt_ms = now_ms - last_update_ms_;
        if (dt_ms == 0) {
            return;
        }
        last_update_ms_ = now_ms;

        // Очікування завершення паузи dead-time
        if (state_ == MotorState::DeadTime) {
            uint32_t now_us = hal_get_time_us();
            if ((now_us - dead_time_start_us_) >= config_.dead_time_us) {
                state_ = MotorState::Running;
                hal_gpio_set_direction(active_dir_);
            } else {
                hal_hbridge_disable_all();
                return;
            }
        }

        float max_delta = (static_cast<float>(config_.slew_rate_pct_s) * static_cast<float>(dt_ms)) / 1000.0f;
        float speed_diff = std::clamp(target_speed_ - current_speed_, -max_delta, max_delta);
        float next_speed = current_speed_ + speed_diff;

        int8_t desired_dir = 0;
        if (next_speed > 0.01f) {
            desired_dir = 1;
        } else if (next_speed < -0.01f) {
            desired_dir = -1;
        }

        // Перехід через нуль з витримкою мертвого часу
        if (desired_dir != 0 && active_dir_ != 0 && desired_dir != active_dir_) {
            hal_hbridge_disable_all();
            current_speed_ = 0.0f;
            active_dir_ = desired_dir;
            state_ = MotorState::DeadTime;
            dead_time_start_us_ = hal_get_time_us();
            return;
        }

        current_speed_ = next_speed;
        active_dir_ = desired_dir;

        if (desired_dir == 0) {
            state_ = MotorState::Idle;
            hal_pwm_set_duty(0.0f);
        } else {
            state_ = MotorState::Running;
            hal_gpio_set_direction(active_dir_);

            float abs_speed = std::abs(current_speed_);
            float deadband = static_cast<float>(config_.deadband_pct);
            float duty = deadband + (abs_speed * (100.0f - deadband) / 100.0f);
            hal_pwm_set_duty(duty);
        }
    }

    MotorState getState() const { return state_; }
    float getCurrentSpeed() const { return current_speed_; }

private:
    MotorTimingConfig config_;
    MotorState        state_;
    float             target_speed_;
    float             current_speed_;
    uint32_t          dead_time_start_us_;
    uint32_t          last_update_ms_;
    int8_t            active_dir_;
};
