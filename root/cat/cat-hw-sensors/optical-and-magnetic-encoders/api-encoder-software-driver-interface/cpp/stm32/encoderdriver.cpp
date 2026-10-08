#include <cstdint>

class EncoderDriver {
private:
    uint32_t cpr_;
    float scale_factor_;
    volatile int32_t raw_counter_{0};
    volatile int32_t prev_counter_{0};
    volatile int64_t total_counts_{0};
    int32_t zero_offset_{0};
    float position_rad_{0.0f};
    float velocity_rad_s_{0.0f};
    uint32_t error_flags_{0};

public:
    explicit EncoderDriver(uint32_t cpr) : cpr_(cpr), scale_factor_(6.28318530718f / cpr) {}
    float get_position_rad() const { return position_rad_; }
    float get_velocity_rad_s() const { return velocity_rad_s_; }
    uint32_t get_errors() const { return error_flags_; }
};
