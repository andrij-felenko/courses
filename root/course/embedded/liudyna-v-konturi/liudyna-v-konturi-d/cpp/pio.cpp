#include "pio.hpp"

#include <algorithm>
#include <cmath>
#include <numbers>

namespace hitl {
namespace {
constexpr float kTrendTc = 0.8f;    // стала часу видалення тренду, с
constexpr float kAmpTc = 0.7f;      // витік огинаючої, с
constexpr float kWindowSec = 1.5f;  // вікно оцінки частоти, с
constexpr float kDegPerRad = 180.0f / std::numbers::pi_v<float>;
}  // namespace

void PioMonitor::Update(float x) noexcept {
    trend_ += (x - trend_) * (dt_ / kTrendTc);
    hp_ = x - trend_;

    amp_ *= std::exp(-dt_ / kAmpTc);
    amp_ = std::max(amp_, std::abs(hp_));

    // Знак міняємо лише коли сигнал вийшов за чверть огинаючої: без
    // гістерезису шум коло нуля дав би фантомну частоту в сотні герц.
    if (amp_ > 1e-5f) {
        int s = 0;
        if (hp_ > 0.25f * amp_) {
            s = 1;
        } else if (hp_ < -0.25f * amp_) {
            s = -1;
        }
        if (s != 0 && s != sign_) {
            if (sign_ != 0) {
                ++crossings_;
            }
            sign_ = s;
        }
    }

    window_t_ += dt_;
    if (window_t_ >= kWindowSec) {
        freq_hz_ = static_cast<float>(crossings_) / (2.0f * window_t_);
        crossings_ = 0;
        window_t_ = 0.0f;
        if (!seeded_) {
            amp_first_ = amp_;
            seeded_ = true;
        }
        amp_last_ = amp_;
    }
}

float PioMonitor::growth() const noexcept {
    return amp_first_ > 1e-4f ? amp_last_ / amp_first_ : 1.0f;
}

bool PioMonitor::IsPio(float amp_threshold) const noexcept {
    return freq_hz_ >= 0.5f && freq_hz_ <= 2.5f && amp_ > amp_threshold;
}

PioCorrelator::PioCorrelator(float dt, float window_sec)
    : leak_{std::exp(-dt / window_sec)} {}

void PioCorrelator::Update(float a, float b) noexcept {
    sxy_ = sxy_ * leak_ + a * b;
    sxx_ = sxx_ * leak_ + a * a;
    syy_ = syy_ * leak_ + b * b;
}

float PioCorrelator::value() const noexcept {
    const float d = std::sqrt(sxx_ * syy_);
    return d > 1e-9f ? sxy_ / d : 0.0f;
}

float PhaseMargin(float pm0_deg, float omega_c, float tau) noexcept {
    return pm0_deg - kDegPerRad * omega_c * tau;
}

float CriticalDelay(float pm0_deg, float omega_c) noexcept {
    return omega_c > 0.0f ? (pm0_deg / kDegPerRad) / omega_c : 0.0f;
}

}  // namespace hitl
