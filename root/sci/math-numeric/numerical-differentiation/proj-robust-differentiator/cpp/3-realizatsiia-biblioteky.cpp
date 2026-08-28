#include <algorithm>
#include <array>
#include <concepts>
#include <numbers>
#include <optional>

/* --- Модульне розгортання кута (Phase Unwrapping C++20) --- */
[[nodiscard]] constexpr float unwrap_angle_diff(float measured_pos, float prev_pos) noexcept {
    constexpr float pi = std::numbers::pi_v<float>;
    constexpr float two_pi = 2.0f * pi;
    float diff = measured_pos - prev_pos;
    while (diff > pi)  diff -= two_pi;
    while (diff < -pi) diff += two_pi;
    return diff;
}

/* --- 1. Спостерігач стану Alpha-Beta-Gamma на C++20 --- */
class TrackingDifferentiator {
public:
    struct State {
        float position{0.0f};
        float velocity{0.0f};
        float acceleration{0.0f};
    };

    struct Gains {
        float alpha{0.6f};
        float beta{0.3f};
        float gamma{0.05f};
        float max_acceleration{10000.0f};
    };

    constexpr explicit TrackingDifferentiator(Gains gains = {}) noexcept
        : gains_{validate_gains(gains)} {}

    void reset(float initial_position = 0.0f) noexcept {
        state_.position = initial_position;
        state_.velocity = 0.0f;
        state_.acceleration = 0.0f;
        initialized_ = true;
    }

    void update(float measured_position, float dt) noexcept {
        if (dt <= 1e-6f || dt > 1.0f) {
            return;
        }

        if (!initialized_) {
            reset(measured_position);
            return;
        }

        /* 1. Кінематичний прогноз */
        const float pos_pred = state_.position + state_.velocity * dt + 0.5f * state_.acceleration * dt * dt;
        const float vel_pred = state_.velocity + state_.acceleration * dt;
        const float acc_pred = state_.acceleration;

        /* 2. Нев'язка вимірювання з захистом від стрибка 2*pi */
        const float residual = unwrap_angle_diff(measured_position, pos_pred);

        /* 3. Корекція за коефіцієнтами спостерігача */
        state_.position = pos_pred + gains_.alpha * residual;
        state_.velocity = vel_pred + (gains_.beta / dt) * residual;
        
        const float raw_acc = acc_pred + (2.0f * gains_.gamma / (dt * dt)) * residual;
        state_.acceleration = std::clamp(raw_acc, -gains_.max_acceleration, gains_.max_acceleration);
    }

    [[nodiscard]] constexpr State state() const noexcept { return state_; }
    [[nodiscard]] constexpr float velocity() const noexcept { return state_.velocity; }
    [[nodiscard]] constexpr float acceleration() const noexcept { return state_.acceleration; }

private:
    static constexpr Gains validate_gains(Gains g) noexcept {
        g.alpha = std::clamp(g.alpha, 0.01f, 1.0f);
        g.beta = std::clamp(g.beta, 0.001f, 1.0f);
        g.gamma = std::clamp(g.gamma, 0.0001f, 1.0f);
        g.max_acceleration = (g.max_acceleration > 0.0f) ? g.max_acceleration : 10000.0f;
        return g;
    }

    Gains gains_;
    State state_{};
    bool initialized_{false};
};

/* --- 2. Диференціатор Тастіна другого порядку (C++20) --- */
class TustinDifferentiator2nd {
public:
    explicit TustinDifferentiator2nd(float cutoff_hz = 10.0f) noexcept
        : cutoff_rad_{2.0f * std::numbers::pi_v<float> * std::max(cutoff_hz, 0.1f)} {}

    [[nodiscard]] float update(float input, float dt) noexcept {
        if (dt <= 1e-6f) {
            return y_prev_;
        }

        constexpr float zeta = 0.70710678f;
        const float w = cutoff_rad_;
        const float c = 2.0f / dt;

        const float a0 = c * c + 2.0f * zeta * w * c + w * w;
        const float b0 = (c * w * w) / a0;
        const float b2 = -b0;
        const float a1 = (2.0f * w * w - 2.0f * c * c) / a0;
        const float a2 = (c * c - 2.0f * zeta * w * c + w * w) / a0;

        const float x0 = input - a1 * x1_ - a2 * x2_;
        const float output = b0 * x0 + b2 * x2_;

        x2_ = x1_;
        x1_ = x0;
        y_prev_ = output;

        return output;
    }

    constexpr void reset() noexcept {
        x1_ = 0.0f;
        x2_ = 0.0f;
        y_prev_ = 0.0f;
    }

    [[nodiscard]] constexpr float value() const noexcept { return y_prev_; }

private:
    float cutoff_rad_{20.0f * std::numbers::pi_v<float>};
    float x1_{0.0f};
    float x2_{0.0f};
    float y_prev_{0.0f};
};
