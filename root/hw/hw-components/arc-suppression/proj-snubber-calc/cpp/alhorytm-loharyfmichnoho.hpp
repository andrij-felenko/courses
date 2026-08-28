#include <iostream>
#include <cmath>
#include <array>
#include <algorithm>

class SnubberDesignEngine {
public:
    static constexpr std::array<double, 24> E24_MANTISSAS = {
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
        3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
    };

    struct Result {
        double c_exact{0.0};
        double c_standard{0.0};
        double r_exact{0.0};
        double r_standard{0.0};
        double p_rating_w{0.0};
    };

    [[nodiscard]] static double quantize_to_e24(double value) noexcept {
        if (value <= 0.0) return 0.0;
        const double exp_val = std::floor(std::log10(value));
        const double mantissa = value / std::pow(10.0, exp_val);

        auto nearest = std::min_element(E24_MANTISSAS.begin(), E24_MANTISSAS.end(),
            [mantissa](double a, double b) noexcept {
                return std::abs(mantissa - a) < std::abs(mantissa - b);
            });

        return *nearest * std::pow(10.0, exp_val);
    }

    [[nodiscard]] static Result compute(double v_cc, double i_load, double l_ind, double f_sw, double v_max) noexcept {
        Result res{};
        const double v_diff_sq = (v_max * v_max) - (v_cc * v_cc);
        const double denom = (v_diff_sq > 0.0) ? v_diff_sq : 1.0;

        res.c_exact = (l_ind * i_load * i_load) / denom;
        res.c_standard = quantize_to_e24(res.c_exact);

        res.r_exact = std::sqrt(l_ind / res.c_standard);
        res.r_standard = quantize_to_e24(res.r_exact);

        // 100 % запас за тепловою потужністю (коефіцієнт 2.0)
        res.p_rating_w = res.c_standard * v_cc * v_cc * f_sw * 2.0;
        return res;
    }
};
