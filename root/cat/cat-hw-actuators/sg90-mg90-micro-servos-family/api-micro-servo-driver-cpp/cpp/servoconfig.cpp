struct ServoConfig {
    uint16_t min_pulse_us{540};
    uint16_t max_pulse_us{2460};
    uint16_t neutral_pulse_us{1500};
    float min_angle_deg{0.0f};
    float max_angle_deg{180.0f};
    float soft_limit_min_deg{5.0f};
    float soft_limit_max_deg{175.0f};
};

class MicroServo {
public:
    enum class Status { Ok, InvalidParam, DriverError };

    explicit MicroServo(void (*pwm_fn)(uint16_t)) : set_pwm_us_(pwm_fn) {}

    Status init(const ServoConfig& cfg) {
        if (!set_pwm_us_) return Status::DriverError;
        if (cfg.min_pulse_us >= cfg.max_pulse_us ||
            cfg.neutral_pulse_us < cfg.min_pulse_us ||
            cfg.neutral_pulse_us > cfg.max_pulse_us ||
            cfg.soft_limit_min_deg < cfg.min_angle_deg ||
            cfg.soft_limit_max_deg > cfg.max_angle_deg ||
            cfg.soft_limit_min_deg >= cfg.soft_limit_max_deg) {
            return Status::InvalidParam;
        }
        cfg_ = cfg;
        current_angle_ = (cfg.soft_limit_min_deg + cfg.soft_limit_max_deg) * 0.5f;
        return Status::Ok;
    }

private:
    ServoConfig cfg_{};
    void (*set_pwm_us_)(uint16_t){nullptr};
    float current_angle_{90.0f};
    bool is_attached_{false};
};
