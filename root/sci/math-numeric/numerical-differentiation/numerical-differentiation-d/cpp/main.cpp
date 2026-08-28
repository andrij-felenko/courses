#include <array>
#include <numbers>
#include <optional>
#include <span>

/* --- 1. Фільтрований диференціатор першого порядку (C++20) --- */
class LowPassDifferentiator {
public:
    constexpr explicit LowPassDifferentiator(float cutoff_hz = 10.0f) noexcept
        : cutoff_hz_{cutoff_hz > 0.1f ? cutoff_hz : 0.1f} {}

    [[nodiscard]] float update(float input, float dt) noexcept {
        if (dt <= 1e-6f) {
            return output_;
        }

        const float tau = 1.0f / (2.0f * std::numbers::pi_v<float> * cutoff_hz_);
        const float alpha = dt / (tau + dt);

        const float raw_diff = (input - prev_input_) / dt;
        prev_input_ = input;

        output_ += alpha * (raw_diff - output_);
        return output_;
    }

    [[nodiscard]] constexpr float value() const noexcept { return output_; }
    constexpr void reset() noexcept {
        prev_input_ = 0.0f;
        output_ = 0.0f;
    }

private:
    float prev_input_{0.0f};
    float output_{0.0f};
    float cutoff_hz_{10.0f};
};

/* --- 2. Шаблонний фільтр Савицького–Голея для 1-ї та 2-ї похідних --- */
template <std::size_t N = 5>
requires (N == 5)
class SavitzkyGolayDifferentiator {
public:
    struct Derivatives {
        float velocity{0.0f};
        float acceleration{0.0f};
    };

    constexpr SavitzkyGolayDifferentiator() noexcept = default;

    void push(float value) noexcept {
        head_ = (head_ + 1) % N;
        buf_[head_] = value;
        if (count_ < N) {
            ++count_;
        }
    }

    [[nodiscard]] std::optional<Derivatives> compute(float dt) const noexcept {
        if (count_ < N || dt <= 1e-6f) {
            return std::nullopt;
        }

        std::array<float, N> y{};
        for (std::size_t i = 0; i < N; ++i) {
            const std::size_t idx = (head_ + 1 + i) % N;
            y[i] = buf_[idx];
        }

        /* Згортка для 1-ї похідної (ваги -2, -1, 0, 1, 2, норма 10) */
        const float vel = (-2.0f * y[0] - 1.0f * y[1] + 1.0f * y[3] + 2.0f * y[4]) / (10.0f * dt);
        
        /* Згортка для 2-ї похідної (ваги 2, -1, -2, -1, 2, норма 7*dt^2) */
        const float acc = (2.0f * y[0] - 1.0f * y[1] - 2.0f * y[2] - 1.0f * y[3] + 2.0f * y[4]) / (7.0f * dt * dt);

        return Derivatives{.velocity = vel, .acceleration = acc};
    }

    constexpr void clear() noexcept {
        buf_.fill(0.0f);
        head_ = 0;
        count_ = 0;
    }

private:
    std::array<float, N> buf_{};
    std::size_t head_{0};
    std::size_t count_{0};
};
