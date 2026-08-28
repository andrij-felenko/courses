// CgAdaptiveMixer.hpp
// Ідіоматична C++ реалізація адаптивного мікшера з безпечною типізацією

#pragma once

#include <array>
#include <algorithm>
#include <cmath>
#include <span>

namespace drone::control {

struct Vector2D {
    float x{0.0f};
    float y{0.0f};
};

struct MixerConfig {
    float arm_length_x{0.22f};    // Базове плече X, м
    float arm_length_y{0.22f};    // Базове плече Y, м
    float k_thrust{15.0f};        // Коефіцієнт тяги, Н / (норм. од.)
    float k_torque{0.02f};        // Коефіцієнт моменту гвинта, м
    float est_time_constant{2.5f};// Постійна часу фільтра оцінювача, с
    float max_cg_offset{0.08f};   // Максимально допустиме зміщення, м
};

class CgAdaptiveMixer {
public:
    static constexpr std::size_t MotorCount = 4;
    using MotorArray = std::array<float, MotorCount>;

    explicit CgAdaptiveMixer(const MixerConfig& config) noexcept
        : config_(config) {}

    void reset() noexcept {
        offset_ = {0.0f, 0.0f};
        thrusts_.fill(0.0f);
        saturated_ = false;
    }

    // Онлайн-оцінка вектора зміщення CG
    void updateEstimator(bool in_steady_hover, float dt) noexcept {
        if (!in_steady_hover || dt <= 0.0f) return;

        const float t_front = thrusts_[0] + thrusts_[2];
        const float t_rear  = thrusts_[1] + thrusts_[3];
        const float t_right = thrusts_[0] + thrusts_[3];
        const float t_left  = thrusts_[1] + thrusts_[2];
        const float total_t = t_front + t_rear;

        if (total_t < 0.2f) return;

        const float raw_dx = config_.arm_length_x * (t_rear - t_front) / total_t;
        const float raw_dy = config_.arm_length_y * (t_left - t_right) / total_t;

        const float alpha = std::clamp(dt / config_.est_time_constant, 0.0f, 1.0f);
        offset_.x += alpha * (raw_dx - offset_.x);
        offset_.y += alpha * (raw_dy - offset_.y);

        offset_.x = std::clamp(offset_.x, -config_.max_cg_offset, config_.max_cg_offset);
        offset_.y = std::clamp(offset_.y, -config_.max_cg_offset, config_.max_cg_offset);
    }

    // Динамічний перерахунок тяги моторів з пріоритетом стабілізації
    void compute(float throttle, float roll_torque, float pitch_torque, float yaw_torque) noexcept {
        // Миттєві плечі моторів відносно зміщеного центру мас
        const float lx0 = config_.arm_length_x - offset_.x;
        const float ly0 = config_.arm_length_y - offset_.y;
        const float lx1 = config_.arm_length_x + offset_.x;
        const float ly1 = config_.arm_length_y + offset_.y;

        const float r_roll  = roll_torque  / (4.0f * config_.k_thrust * config_.arm_length_y);
        const float r_pitch = pitch_torque / (4.0f * config_.k_thrust * config_.arm_length_x);
        const float r_yaw   = yaw_torque   / (4.0f * config_.k_thrust * config_.k_torque);

        const float base = throttle * 0.25f;
        const float sum_lx = lx0 + lx1;
        const float sum_ly = ly0 + ly1;

        // Коригувальні геометричні коефіцієнти
        const float scale_0 = (lx1 / sum_lx) * (ly1 / sum_ly) * 4.0f;
        const float scale_1 = (lx0 / sum_lx) * (ly0 / sum_ly) * 4.0f;
        const float scale_2 = (lx1 / sum_lx) * (ly0 / sum_ly) * 4.0f;
        const float scale_3 = (lx0 / sum_lx) * (ly1 / sum_ly) * 4.0f;

        MotorArray raw_t = {
            base * scale_0 - r_roll + r_pitch - r_yaw,
            base * scale_1 + r_roll - r_pitch - r_yaw,
            base * scale_2 + r_roll + r_pitch + r_yaw,
            base * scale_3 - r_roll - r_pitch + r_yaw
        };

        // Денасичення (Desaturation) для збереження керуючих моментів
        float min_val = *std::min_element(raw_t.begin(), raw_t.end());
        float max_val = *std::max_element(raw_t.begin(), raw_t.end());

        saturated_ = false;

        if (max_val > 1.0f) {
            const float excess = max_val - 1.0f;
            for (auto& val : raw_t) val -= excess;
            saturated_ = true;
        }

        if (min_val < 0.0f) {
            for (auto& val : raw_t) val = std::max(val, 0.0f);
            saturated_ = true;
        }

        for (std::size_t i = 0; i < MotorCount; ++i) {
            thrusts_[i] = std::clamp(raw_t[i], 0.0f, 1.0f);
        }
    }

    [[nodiscard]] Vector2D getEstimatedOffset() const noexcept { return offset_; }
    [[nodiscard]] std::span<const float, MotorCount> getThrusts() const noexcept { return thrusts_; }
    [[nodiscard]] bool isSaturated() const noexcept { return saturated_; }

private:
    MixerConfig config_;
    Vector2D offset_{};
    MotorArray thrusts_{};
    bool saturated_{false};
};

} // namespace drone::control
