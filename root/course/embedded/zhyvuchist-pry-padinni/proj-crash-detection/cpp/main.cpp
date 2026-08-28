#include <array>
#include <cmath>
#include <algorithm>
#include <cstdint>

struct ImuSample {
    float ax_g{0.0f};
    float ay_g{0.0f};
    float az_g{0.0f};
    float gx_dps{0.0f};
    float gy_dps{0.0f};
    float gz_dps{0.0f};
};

class CrashDetector {
public:
    struct Config {
        float accel_threshold_g{15.0f};
        float gyro_threshold_dps{1200.0f};
        uint8_t debounce_samples{3};
    };

    explicit constexpr CrashDetector(Config cfg = Config{}) : config_(cfg) {}

    [[nodiscard]] bool update(const ImuSample& imu, bool is_armed) noexcept {
        if (!is_armed) {
            impact_counter_ = 0;
            return false;
        }

        if (disarm_latched_) {
            return true;
        }

        const float accel_sq = (imu.ax_g * imu.ax_g) + 
                               (imu.ay_g * imu.ay_g) + 
                               (imu.az_g * imu.az_g);
        const float accel_mag = std::sqrt(accel_sq);

        const float gyro_max = std::max({std::abs(imu.gx_dps), 
                                         std::abs(imu.gy_dps), 
                                         std::abs(imu.gz_dps)});

        const bool is_impact = (accel_mag >= config_.accel_threshold_g);
        const bool is_spin = (gyro_max >= config_.gyro_threshold_dps);

        if (is_impact || is_spin) {
            if (impact_counter_ < 255) {
                ++impact_counter_;
            }
        } else if (impact_counter_ > 0) {
            --impact_counter_;
        }

        if (impact_counter_ >= config_.debounce_samples) {
            is_crashed_ = true;
            disarm_latched_ = true;
            return true;
        }

        return false;
    }

    [[nodiscard]] bool is_crashed() const noexcept { return is_crashed_; }
    [[nodiscard]] bool is_latched() const noexcept { return disarm_latched_; }

    void reset() noexcept {
        impact_counter_ = 0;
        is_crashed_ = false;
        disarm_latched_ = false;
    }

private:
    Config config_;
    uint8_t impact_counter_{0};
    bool is_crashed_{false};
    bool disarm_latched_{false};
};
