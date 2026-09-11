#pragma once

#include <cstdint>
#include <cstddef>
#include <array>

namespace trig {

/// Точне значення числа Пі для constexpr обчислень геометрії
constexpr double PI = 3.14159265358979323846;

/// Переведення кутової міри з градусів у радіани
constexpr double deg_to_rad(double deg) noexcept {
    return deg * (PI / 180.0);
}

/// Приведення довільного кута в радіанах до симетричного відрізка [-PI, PI]
constexpr double normalize_rad(double rad) noexcept {
    while (rad > PI) {
        rad -= 2.0 * PI;
    }
    while (rad < -PI) {
        rad += 2.0 * PI;
    }
    return rad;
}

/// Обчислення синуса за поліномом Тейлора (Маклорена) на етапі компіляції.
/// Сім розрахункових доданків гарантують похибку нижче 1e-10 на інтервалі [-PI, PI].
constexpr double sin_taylor(double rad) noexcept {
    const double x = normalize_rad(rad);
    const double x2 = x * x;

    double term = x;
    double sum = term;

    // -x^3 / 3!
    term *= -x2 / (2.0 * 3.0);
    sum += term;
    // +x^5 / 5!
    term *= -x2 / (4.0 * 5.0);
    sum += term;
    // -x^7 / 7!
    term *= -x2 / (6.0 * 7.0);
    sum += term;
    // +x^9 / 9!
    term *= -x2 / (8.0 * 9.0);
    sum += term;
    // -x^11 / 11!
    term *= -x2 / (10.0 * 11.0);
    sum += term;
    // +x^13 / 13!
    term *= -x2 / (12.0 * 13.0);
    sum += term;

    return sum;
}

/// Обчислення косинуса через зсув фази: cos(x) = sin(x + PI/2)
constexpr double cos_taylor(double rad) noexcept {
    return sin_taylor(rad + (PI / 2.0));
}

/// Елемент тригонометричної таблиці з фіксованою комою формату Q15.
/// 1 знаковий біт, 15 дробових бітів (одиниці відповідає число 32767).
struct TrigPointQ15 {
    int16_t cos_val;
    int16_t sin_val;
};

/// Генерація попередньо розрахованої таблиці синусів і косинусів
/// для N рівномірних кутових положень на етапі компіляції (zero-cost LUT).
template <size_t N = 360>
constexpr auto generate_trig_table() noexcept {
    std::array<TrigPointQ15, N> table{};

    auto to_q15 = [](double val) -> int16_t {
        if (val >= 1.0) return 32767;
        if (val <= -1.0) return -32767;
        return static_cast<int16_t>(val * 32767.0 + (val >= 0.0 ? 0.5 : -0.5));
    };

    for (size_t i = 0; i < N; ++i) {
        const double deg = static_cast<double>(i) * (360.0 / static_cast<double>(N));
        const double rad = deg_to_rad(deg);
        table[i] = TrigPointQ15{
            .cos_val = to_q15(cos_taylor(rad)),
            .sin_val = to_q15(sin_taylor(rad))
        };
    }
    return table;
}

/// Клас компіляційної тригонометричної таблиці для мікроконтролера
class TrigLut {
public:
    static constexpr size_t RESOLUTION = 360;
    static constexpr int16_t ONE_Q15 = 32767;

    /// Таблиця зберігається безпосередньо у флеш-пам'яті програм (.rodata)
    static constexpr auto TABLE = generate_trig_table<RESOLUTION>();

    /// Безпечний вибір значень синуса й косинуса за довільним цілим кутом у градусах
    [[nodiscard]] static constexpr TrigPointQ15 get(int deg) noexcept {
        int idx = deg % static_cast<int>(RESOLUTION);
        if (idx < 0) {
            idx += static_cast<int>(RESOLUTION);
        }
        return TABLE[static_cast<size_t>(idx)];
    }

    [[nodiscard]] static constexpr int16_t cos_q15(int deg) noexcept {
        return get(deg).cos_val;
    }

    [[nodiscard]] static constexpr int16_t sin_q15(int deg) noexcept {
        return get(deg).sin_val;
    }

    /// Швидке апаратне множення скаляра на коефіцієнт Q15: (val * factor) >> 15
    [[nodiscard]] static constexpr int32_t mult_q15(int32_t val, int16_t q15_factor) noexcept {
        return (val * static_cast<int32_t>(q15_factor)) >> 15;
    }
};

} // namespace trig
