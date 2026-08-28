#include <iostream>
#include <cmath>
#include <cstdint>
#include <concepts>

struct Fraction {
    int32_t num{0};
    int32_t den{1};

    [[nodiscard]] double value() const noexcept {
        return static_cast<double>(num) / den;
    }
};

/* Шаблонний бінарний пошук Фарея для довільних типів із рухомою комою (C++20) */
template <std::floating_point FloatType>
[[nodiscard]] Fraction find_best_rational_approximation(FloatType target_val, int32_t max_den) noexcept {
    Fraction left{0, 1};
    Fraction right{1, 1};

    while (true) {
        int32_t med_num = left.num + right.num;
        int32_t med_den = left.den + right.den;

        if (med_den > max_den) {
            break;
        }

        FloatType med_val = static_cast<FloatType>(med_num) / med_den;

        if (std::abs(target_val - med_val) < FloatType(1e-15)) {
            return {med_num, med_den};
        }

        if (target_val > med_val) {
            left = {med_num, med_den};
        } else {
            right = {med_num, med_den};
        }
    }

    FloatType err_left = std::abs(target_val - left.value());
    FloatType err_right = std::abs(target_val - right.value());

    return (err_left <= err_right) ? left : right;
}
