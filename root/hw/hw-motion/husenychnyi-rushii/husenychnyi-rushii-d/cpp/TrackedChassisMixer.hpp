// TrackedChassisMixer.hpp — ідіоматичний контролер керування гусеничним шасі на C++20
#pragma once
#include <algorithm>
#include <cmath>

struct TrackVelocities {
    float left{0.0f};   // Діапазон [-1.0f ... +1.0f]
    float right{0.0f};  // Діапазон [-1.0f ... +1.0f]
};

struct MixerConfig {
    float max_accel{2.5f};          // Максимальне лінійне прискорення (1/c)
    float current_limit_a{40.0f};   // Струмовий поріг початку троттлінгу (А)
    float derating_slope{15.0f};    // Крутизна струмового спаду (А)
};

class TrackedChassisMixer {
public:
    explicit constexpr TrackedChassisMixer(MixerConfig config = {}) noexcept
        : config_{config} {}

    [[nodiscard]] TrackVelocities update(float throttle,
                                         float steering,
                                         float measured_current_a,
                                         float dt) noexcept {
        // 1. Нормалізація вхідних сигналів
        const float th = std::clamp(throttle, -1.0f, 1.0f);
        const float st = std::clamp(steering, -1.0f, 1.0f);

        // 2. Розрахунок швидкостей бортів
        float v_left = th + st;
        float v_right = th - st;

        // 3. Антинасичення з абсолютним пріоритетом збереження радіуса повороту
        const float max_mag = std::max(std::abs(v_left), std::abs(v_right));
        if (max_mag > 1.0f) {
            v_left /= max_mag;
            v_right /= max_mag;
        }

        // 4. Динамічний струмовий троттлінг для захисту MOSFET та обмоток
        if (measured_current_a > config_.current_limit_a) {
            const float over_current = measured_current_a - config_.current_limit_a;
            const float derating_factor = 1.0f - std::clamp(over_current / config_.derating_slope, 0.0f, 0.75f);
            v_left *= derating_factor;
            v_right *= derating_factor;
        }

        // 5. Двосторонній фільтр темпу зміни швидкості (Slew Rate Limiting)
        const float max_step = config_.max_accel * dt;
        
        const float delta_l = std::clamp(v_left - left_velocity_, -max_step, max_step);
        left_velocity_ += delta_l;

        const float delta_r = std::clamp(v_right - right_velocity_, -max_step, max_step);
        right_velocity_ += delta_r;

        return TrackVelocities{.left = left_velocity_, .right = right_velocity_};
    }

    void reset() noexcept {
        left_velocity_ = 0.0f;
        right_velocity_ = 0.0f;
    }

    [[nodiscard]] constexpr float left() const noexcept { return left_velocity_; }
    [[nodiscard]] constexpr float right() const noexcept { return right_velocity_; }

private:
    MixerConfig config_;
    float left_velocity_{0.0f};
    float right_velocity_{0.0f};
};
