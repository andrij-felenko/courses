#pragma once

// Рівняння Каллендара-Ван Дюзена (характеристика DIN/IEC 60751).
// Чиста математика без жодного заліза — тому живе цілком у заголовку.

#include <cmath>
#include <expected>

namespace pt100 {

enum class Error {
    OutOfRange  // опір поза паспортним діапазоном -200…850 °C
};

inline constexpr float kR0 = 100.0F;
inline constexpr float kA  = 3.9083e-3F;
inline constexpr float kB  = -5.7750e-7F;
inline constexpr float kC  = -4.1830e-12F;

// Паспортні краї датчика: 18.52 Ом при -200 °C, 390.48 Ом при 850 °C
inline constexpr float kMinOhms = 18.0F;
inline constexpr float kMaxOhms = 391.0F;

// Пряме рівняння: температура -> опір. Кубічний член визначено
// лише для від'ємного боку шкали.
[[nodiscard]] inline float resistanceAt(float celsius) noexcept {
    const float t2 = celsius * celsius;
    const float t3 = t2 * celsius;
    const float cubic = (celsius < 0.0F) ? kC * (celsius - 100.0F) * t3 : 0.0F;
    return kR0 * (1.0F + kA * celsius + kB * t2 + cubic);
}

// Обернена задача: опір -> температура.
[[nodiscard]] inline std::expected<float, Error> celsiusAt(float ohms) noexcept {
    if (!(ohms >= kMinOhms) || !(ohms <= kMaxOhms)) {
        return std::unexpected(Error::OutOfRange);  // заразом відсіює NaN
    }

    // Вище нуля рівняння квадратне й розв'язується аналітично
    const float z = 1.0F - (ohms / kR0);
    const float discriminant = (kA * kA) - (4.0F * kB * z);
    if (discriminant < 0.0F) {
        return std::unexpected(Error::OutOfRange);
    }

    float celsius = (-kA + std::sqrt(discriminant)) / (2.0F * kB);

    // Нижче нуля до рівняння додається кубічний член: аналітичний корінь
    // лишається тільки першим наближенням, яке дотягує метод Ньютона-Рафсона.
    if (celsius < 0.0F) {
        constexpr int   kMaxSteps = 5;
        constexpr float kEpsilon  = 1.0e-4F;

        for (int step = 0; step < kMaxSteps; ++step) {
            const float t2 = celsius * celsius;
            const float t3 = t2 * celsius;

            // dR/dT = R0·(A + 2B·T - 300C·T² + 4C·T³)
            const float slope = kR0 * (kA + 2.0F * kB * celsius
                                       - 300.0F * kC * t2
                                       + 4.0F * kC * t3);
            if (std::fabs(slope) < 1.0e-9F) {
                return std::unexpected(Error::OutOfRange);
            }

            const float correction = (resistanceAt(celsius) - ohms) / slope;
            celsius -= correction;
            if (std::fabs(correction) < kEpsilon) {
                break;  // два-три кроки дають похибку менше за 0.001 °C
            }
        }
    }

    if (celsius < -200.0F || celsius > 850.0F) {
        return std::unexpected(Error::OutOfRange);
    }
    return celsius;
}

}  // namespace pt100
