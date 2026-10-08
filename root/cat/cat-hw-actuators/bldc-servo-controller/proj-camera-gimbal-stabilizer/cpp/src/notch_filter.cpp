#include "notch_filter.hpp"
#include <cmath>

namespace gimbal {

static constexpr float PI = 3.14159265358979323846f;

NotchFilter::NotchFilter(float center_freq_hz, float bandwidth_hz, float sample_rate_hz) {
    configure(center_freq_hz, bandwidth_hz, sample_rate_hz);
}

void NotchFilter::configure(float center_freq_hz, float bandwidth_hz, float sample_rate_hz) {
    if (sample_rate_hz <= 0.0f || center_freq_hz <= 0.0f || bandwidth_hz <= 0.0f) {
        reset();
        return;
    }

    // Нормалізована кутова частота та ширини смуги
    float w0 = 2.0f * PI * center_freq_hz / sample_rate_hz;
    float ww = 2.0f * PI * bandwidth_hz / sample_rate_hz;

    // Розрахунок параметрів білінійного перетворення
    float alpha = std::tan(ww / 2.0f);
    float beta = std::cos(w0);

    float norm = 1.0f / (1.0f + alpha);

    // Нормалізовані коефіцієнти другого порядку (biquad)
    b0_ = norm;
    b1_ = -2.0f * beta * norm;
    b2_ = norm;
    a1_ = -2.0f * beta * norm;
    a2_ = (1.0f - alpha) * norm;

    configured_ = true;
    reset();
}

float NotchFilter::update(float input) {
    if (!configured_) {
        return input;
    }

    // Обчислення прямої форми II (Direct Form II):
    // w[n] = x[n] - a1 * w[n-1] - a2 * w[n-2]
    // y[n] = b0 * w[n] + b1 * w[n-1] + b2 * w[n-2]
    float w0 = input - a1_ * w1_ - a2_ * w2_;
    float output = b0_ * w0 + b1_ * w1_ + b2_ * w2_;

    // Зсув лінії затримок стану
    w2_ = w1_;
    w1_ = w0;

    return output;
}

void NotchFilter::reset() {
    w1_ = 0.0f;
    w2_ = 0.0f;
}

} // namespace gimbal
