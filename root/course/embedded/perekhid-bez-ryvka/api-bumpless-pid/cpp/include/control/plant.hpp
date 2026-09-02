#pragma once

/*
 * Модель об'єкта керування для демонстрації: вертикальний канал
 * мультикоптера. Вимірювана величина — швидкість набору висоти [м/с],
 * керування — нормований хід газу [0..1].
 */

#include <cstdint>

namespace demo {

class ClimbRatePlant {
public:
    explicit ClimbRatePlant(float hover_throttle) noexcept
        : hover_throttle_{hover_throttle} {}

    /// Один крок інтегрування; повертає нову істинну швидкість набору.
    float step(float throttle, float dt) noexcept;

    /*
     * Відлік давача: істинна швидкість плюс згладжений шум.
     * `fault` імітує зрив обміну на шині — тоді повертається NaN.
     */
    [[nodiscard]] float sample(bool fault) noexcept;

    [[nodiscard]] float altitude() const noexcept { return altitude_; }
    [[nodiscard]] float climb_rate() const noexcept { return climb_rate_; }
    [[nodiscard]] float hover_throttle() const noexcept { return hover_throttle_; }

private:
    [[nodiscard]] float white() noexcept;

    float altitude_{0.0f};        // м
    float climb_rate_{0.0f};      // м/с — істинна швидкість набору
    float hover_throttle_{0.55f}; // хід газу, на якому тяга дорівнює вазі
    float thrust_gain_{12.0f};    // м/с² на одиницю ходу газу понад завислість
    float drag_{0.8f};            // 1/с — усталена швидкість 15 м/с на одиницю ходу
    float gust_{0.0f};            // м/с² — стале збурення
    float noise_{0.0f};           // м/с — згладжений шум давача
    std::uint32_t rng_{0x13579BDFu};
};

} // namespace demo
