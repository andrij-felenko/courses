class ContinuousServoDriver {
public:
    ContinuousServoDriver(servo_continuous_config_t cfg, float max_accel, uint32_t timeout_ms)
        : cfg_(cfg), max_accel_(max_accel), timeout_ms_(timeout_ms) {}

    void set_speed(float speed, uint32_t now_ms) {
        target_speed_ = (speed > 1.0f) ? 1.0f : ((speed < -1.0f) ? -1.0f : speed);
        last_cmd_ms_ = now_ms;
    }

    void update(uint32_t now_ms, uint32_t dt_ms) {
        if (now_ms - last_cmd_ms_ > timeout_ms_) {
            target_speed_ = 0.0f;
        }
        float step = max_accel_ * (dt_ms / 1000.0f);
        float diff = target_speed_ - current_speed_;
        if (diff > step) current_speed_ += step;
        else if (diff < -step) current_speed_ -= step;
        else current_speed_ = target_speed_;
        servo_continuous_set_speed(&cfg_, current_speed_);
    }

private:
    servo_continuous_config_t cfg_;
    float current_speed_{0.0f};
    float target_speed_{0.0f};
    float max_accel_;
    uint32_t timeout_ms_;
    uint32_t last_cmd_ms_{0};
};
