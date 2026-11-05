#include <stdint.h>
#include <cmath>

class EncoderEstimator {
public:
    constexpr static float kPi = 3.14159265358979323846f;

    EncoderEstimator(uint32_t cpr, float wheel_radius_m, float filter_alpha)
        : cpr_(cpr), wheel_radius_m_(wheel_radius_m), filter_alpha_(filter_alpha) {}

    void update(int64_t current_ticks, float dt_sec) {
        total_ticks_ = current_ticks;
        const int64_t delta_ticks = current_ticks - prev_ticks_;
        prev_ticks_ = current_ticks;

        const float delta_angle = (2.0f * kPi * static_cast<float>(delta_ticks)) / static_cast<float>(cpr_);
        const float raw_velocity = delta_angle / dt_sec;

        // Експоненційне згладжування швидкості
        filtered_velocity_ = (filter_alpha_ * raw_velocity) + 
                             ((1.0f - filter_alpha_) * filtered_velocity_);
    }

    [[nodiscard]] float get_angle_rad() const {
        return (2.0f * kPi * static_cast<float>(total_ticks_)) / static_cast<float>(cpr_);
    }

    [[nodiscard]] float get_angle_deg() const {
        return (360.0f * static_cast<float>(total_ticks_)) / static_cast<float>(cpr_);
    }

    [[nodiscard]] float get_linear_distance_m() const {
        return get_angle_rad() * wheel_radius_m_;
    }

    [[nodiscard]] float get_angular_velocity_rad_s() const {
        return filtered_velocity_;
    }

    [[nodiscard]] float get_rpm() const {
        return (filtered_velocity_ * 60.0f) / (2.0f * kPi);
    }

private:
    uint32_t cpr_;
    float wheel_radius_m_;
    float filter_alpha_;
    int64_t total_ticks_{0};
    int64_t prev_ticks_{0};
    float filtered_velocity_{0.0f};
};
