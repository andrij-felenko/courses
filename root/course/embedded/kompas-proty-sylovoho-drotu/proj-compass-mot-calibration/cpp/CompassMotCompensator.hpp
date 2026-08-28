/* CompassMotCompensator.hpp - Idiomatic C++20 Compass-Mot Engine */
#pragma once

#include <array>
#include <cmath>
#include <cstdint>
#include <numbers>
#include <optional>
#include <span>

namespace navigation {

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr Vector3f operator-(const Vector3f& other) const noexcept {
        return {x - other.x, y - other.y, z - other.z};
    }

    [[nodiscard]] constexpr Vector3f operator*(float scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }

    [[nodiscard]] float length() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
};

class CompassMotCompensator {
public:
    struct CalibrationResult {
        Vector3f coefficients{};
        float interference_percent{0.0f};
        uint32_t sample_count{0};
    };

    explicit CompassMotCompensator(Vector3f coeffs = {},
                                  float dt_seconds = 0.01f,
                                  float filter_cutoff_hz = 15.0f,
                                  float max_current_limit = 250.0f) noexcept
        : k_current_(coeffs),
          max_current_(max_current_limit),
          is_active_(coeffs.length() > 1e-5f) {
        update_filter_alpha(dt_seconds, filter_cutoff_hz);
    }

    void set_filter_parameters(float dt_seconds, float filter_cutoff_hz) noexcept {
        update_filter_alpha(dt_seconds, filter_cutoff_hz);
    }

    void set_coefficients(const Vector3f& coeffs) noexcept {
        k_current_ = coeffs;
        is_active_ = (k_current_.length() > 1e-5f);
    }

    [[nodiscard]] constexpr const Vector3f& coefficients() const noexcept {
        return k_current_;
    }

    [[nodiscard]] constexpr bool is_active() const noexcept {
        return is_active_;
    }

    void reset() noexcept {
        current_lpf_ = 0.0f;
    }

    /* Потокова корекція вимірювання за струмом */
    [[nodiscard]] Vector3f compensate(const Vector3f& raw_field,
                                      float measured_current_amps) noexcept {
        if (!is_active_ || measured_current_amps < 0.0f || measured_current_amps > max_current_) {
            return raw_field;
        }

        // Оновлення IIR фільтра струму для усунення високочастотного шуму шунта
        current_lpf_ += lpf_alpha_ * (measured_current_amps - current_lpf_);

        return {
            raw_field.x - k_current_.x * current_lpf_,
            raw_field.y - k_current_.y * current_lpf_,
            raw_field.z - k_current_.z * current_lpf_
        };
    }

    /* Клас-накопичувач для проведення наземного регресійного калібрування */
    class Calibrator {
    public:
        explicit Calibrator(const Vector3f& baseline_field) noexcept
            : baseline_(baseline_field) {}

        void feed(float current_amps, const Vector3f& mag_reading) noexcept {
            if (current_amps < 0.0f) return;

            const Vector3f delta = mag_reading - baseline_;
            sum_i_    += current_amps;
            sum_i2_   += current_amps * current_amps;
            sum_bx_   += delta.x;
            sum_by_   += delta.y;
            sum_bz_   += delta.z;
            sum_i_bx_ += current_amps * delta.x;
            sum_i_by_ += current_amps * delta.y;
            sum_i_bz_ += current_amps * delta.z;
            ++count_;
        }

        [[nodiscard]] std::optional<CalibrationResult> solve() const noexcept {
            if (count_ < 30) {
                return std::nullopt;
            }

            const float n = static_cast<float>(count_);
            const float denom = n * sum_i2_ - sum_i_ * sum_i_;
            if (std::abs(denom) < 1e-6f) {
                return std::nullopt;
            }

            CalibrationResult res;
            res.coefficients.x = (n * sum_i_bx_ - sum_i_ * sum_bx_) / denom;
            res.coefficients.y = (n * sum_i_by_ - sum_i_ * sum_by_) / denom;
            res.coefficients.z = (n * sum_i_bz_ - sum_i_ * sum_bz_) / denom;
            res.sample_count = count_;

            const float base_mag = baseline_.length();
            const float test_current = 100.0f; // Оцінка при струмі форсажу 100 А
            if (base_mag > 1.0f) {
                res.interference_percent = (res.coefficients.length() * test_current / base_mag) * 100.0f;
            }

            return res;
        }

    private:
        Vector3f baseline_;
        float sum_i_{0.0f};
        float sum_i2_{0.0f};
        float sum_bx_{0.0f};
        float sum_by_{0.0f};
        float sum_bz_{0.0f};
        float sum_i_bx_{0.0f};
        float sum_i_by_{0.0f};
        float sum_i_bz_{0.0f};
        uint32_t count_{0};
    };

private:
    void update_filter_alpha(float dt_sec, float cutoff_hz) noexcept {
        const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * cutoff_hz);
        lpf_alpha_ = dt_sec / (rc + dt_sec);
    }

    Vector3f k_current_{};
    float lpf_alpha_{0.5f};
    float current_lpf_{0.0f};
    float max_current_{250.0f};
    bool is_active_{false};
};

} // namespace navigation
