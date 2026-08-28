/* MagCurrentCompensator.hpp - Idiomatic C++20 Implementation */
#pragma once

#include <array>
#include <cmath>
#include <numbers>
#include <span>

namespace flight_control {

struct MagVector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr MagVector3f operator-(const MagVector3f& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }

    [[nodiscard]] constexpr MagVector3f operator*(float scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }

    [[nodiscard]] float length_squared() const noexcept {
        return x * x + y * y + z * z;
    }
};

class MagCurrentCompensator {
public:
    constexpr explicit MagCurrentCompensator(MagVector3f compensation_coeffs = {},
                                             float dt_seconds = 0.01f,
                                             float filter_cutoff_hz = 15.0f,
                                             float max_current_limit = 250.0f) noexcept
        : k_coeffs_(compensation_coeffs),
          max_current_(max_current_limit),
          is_active_(compensation_coeffs.length_squared() > 1e-6f) {
        set_filter_parameters(dt_seconds, filter_cutoff_hz);
    }

    void set_filter_parameters(float dt_seconds, float filter_cutoff_hz) noexcept {
        const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * filter_cutoff_hz);
        lpf_alpha_ = dt_seconds / (rc + dt_seconds);
    }

    void set_coefficients(const MagVector3f& coeffs) noexcept {
        k_coeffs_ = coeffs;
        is_active_ = (k_coeffs_.length_squared() > 1e-6f);
    }

    void reset() noexcept {
        filtered_current_ = 0.0f;
    }

    [[nodiscard]] constexpr bool is_active() const noexcept {
        return is_active_;
    }

    [[nodiscard]] constexpr const MagVector3f& coefficients() const noexcept {
        return k_coeffs_;
    }

    /**
     * Потокова корекція вектора магнітометра
     * @param uncompensated_field Вектор магнітометра після калібрування заліза
     * @param battery_current_amps Струм від датчика Power Module
     * @return Скомпенсований вектор поля Землі
     */
    [[nodiscard]] MagVector3f process(const MagVector3f& uncompensated_field,
                                      float battery_current_amps) noexcept {
        // Захисна перевірка на обрив чи насичення сенсора струму
        if (!is_active_ || battery_current_amps < 0.0f || battery_current_amps > max_current_) {
            return uncompensated_field;
        }

        // Оновлення експоненційного фільтра низьких частот струму
        filtered_current_ += lpf_alpha_ * (battery_current_amps - filtered_current_);

        // B_corr = B_raw - k_I * I_filt
        return {
            uncompensated_field.x - k_coeffs_.x * filtered_current_,
            uncompensated_field.y - k_coeffs_.y * filtered_current_,
            uncompensated_field.z - k_coeffs_.z * filtered_current_
        };
    }

private:
    MagVector3f k_coeffs_{};
    float filtered_current_{0.0f};
    float lpf_alpha_{0.5f};
    float max_current_{250.0f};
    bool is_active_{false};
};

} // namespace flight_control
