#pragma once

#include <cstdint>
#include <algorithm>

/// Клас-контролер фізичного експоненційного демпфування коливань стрілки приладу.
/// Моделює динаміку другого порядку: пружне повернення торсіонної пружини
/// та в'язке демпфування електродинамічного гальмування стрілочного механізму.
class DampedPointer {
public:
    struct Config {
        float min_angle_deg{135.0f};  // Початкове положення шкали (південно-західний сектор)
        float max_angle_deg{405.0f};  // Кінцеве положення шкали (південно-східний сектор, розмах 270°)
        float natural_freq{16.0f};    // Власна частота omega_0 (рад/с), задає пружність відгуку
        float damping_ratio{0.74f};   // Коефіцієнт демпфування zeta (0.7-0.8 для плавного реалістичного відскоку)
    };

    explicit constexpr DampedPointer(const Config& cfg = {}) noexcept
        : config_(cfg),
          current_angle_(cfg.min_angle_deg),
          target_angle_(cfg.min_angle_deg),
          angular_velocity_(0.0f) {}

    /// Встановлення цільового значення приладу у нормалізованому діапазоні [0.0, 1.0]
    void set_target_normalized(float norm_val) noexcept {
        norm_val = std::clamp(norm_val, 0.0f, 1.0f);
        target_angle_ = config_.min_angle_deg + norm_val * (config_.max_angle_deg - config_.min_angle_deg);
    }

    /// Пряме встановлення цільового кута в градусах
    void set_target_angle(float deg) noexcept {
        target_angle_ = std::clamp(deg, config_.min_angle_deg, config_.max_angle_deg);
    }

    /// Крок чисельного інтегрування динамічної моделі за методом напівнеявного Ейлера.
    /// Забезпечує збереження фазового об'єму та стійкість без накопичення енергії.
    void update(float dt_seconds) noexcept {
        // Диференціальне рівняння гармонічного осцилятора із затуханням:
        // d2(theta)/dt2 = -omega_0^2 * (theta - target) - 2 * zeta * omega_0 * d(theta)/dt
        const float displacement = current_angle_ - target_angle_;
        const float spring_torque = -config_.natural_freq * config_.natural_freq * displacement;
        const float damping_torque = -2.0f * config_.damping_ratio * config_.natural_freq * angular_velocity_;
        const float total_accel = spring_torque + damping_torque;

        // Інтегрування швидкості та позиції
        angular_velocity_ += total_accel * dt_seconds;
        current_angle_ += angular_velocity_ * dt_seconds;

        // Моделювання пружно-непружного зіткнення з механічними кінцевими упорами циферблата
        constexpr float margin = 2.0f;
        const float hard_min = config_.min_angle_deg - margin;
        const float hard_max = config_.max_angle_deg + margin;

        if (current_angle_ < hard_min) {
            current_angle_ = hard_min;
            if (angular_velocity_ < 0.0f) {
                angular_velocity_ = -angular_velocity_ * 0.22f; // частковий відскік від упору
            }
        } else if (current_angle_ > hard_max) {
            current_angle_ = hard_max;
            if (angular_velocity_ > 0.0f) {
                angular_velocity_ = -angular_velocity_ * 0.22f;
            }
        }
    }

    /// Поточний дійсний кут стрілки
    [[nodiscard]] constexpr float angle_deg() const noexcept {
        return current_angle_;
    }

    /// Поточний кут стрілки, округлений до найближчого цілого градуса для вибірки з LUT
    [[nodiscard]] constexpr int angle_deg_int() const noexcept {
        return static_cast<int>(current_angle_ + (current_angle_ >= 0.0f ? 0.5f : -0.5f));
    }

    /// Цільовий кут покажчика
    [[nodiscard]] constexpr float target_angle() const noexcept {
        return target_angle_;
    }

    /// Миттєва кутова швидкість руху стрілки (град/с)
    [[nodiscard]] constexpr float velocity() const noexcept {
        return angular_velocity_;
    }

    /// Миттєве позиціонування стрілки без інерційних коливань
    void reset(float angle_deg) noexcept {
        current_angle_ = angle_deg;
        target_angle_ = angle_deg;
        angular_velocity_ = 0.0f;
    }

private:
    Config config_;
    float current_angle_;
    float target_angle_;
    float angular_velocity_;
};
