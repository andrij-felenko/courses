#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <algorithm>

constexpr double K_BOLTZMANN = 8.61733e-5; // еВ/К
constexpr double EG_SILICON  = 1.12;       // еВ

struct DiodeParams {
    double v_br0;     // Напруга пробою при 25 °C (В)
    double tc_v;      // Температурний коефіцієнт (1/°C)
    double i_s0;      // Зворотний струм витоку при 25 °C (А)
    double n_miller;  // Показник степеня Міллера
    double r_series;  // Внутрішній опір кристала (Ом)
};

class BreakdownSimulator {
public:
    explicit BreakdownSimulator(DiodeParams params) : params_(params) {}

    [[nodiscard]] double calculateReverseCurrent(double v_d, double temp_c) const {
        if (v_d <= 0.0) return 0.0;

        const double t_kelvin = temp_c + 273.15;
        constexpr double t0_kelvin = 298.15;

        const double i_s = params_.i_s0 * std::pow(t_kelvin / t0_kelvin, 3.0) *
                           std::exp(-(EG_SILICON / (2.0 * K_BOLTZMANN * t_kelvin)) * (1.0 - t_kelvin / t0_kelvin));

        const double v_br = params_.v_br0 * (1.0 + params_.tc_v * (temp_c - 25.0));

        if (v_d >= v_br) {
            const double v_over = v_d - v_br;
            return (i_s * 1000.0) + (v_over / params_.r_series);
        }

        const double ratio = v_d / v_br;
        double m_factor = 1.0 / (1.0 - std::pow(ratio, params_.n_miller));
        m_factor = std::min(m_factor, 1e4);

        return i_s * m_factor;
    }

    [[nodiscard]] std::pair<double, double> solveOperatingPoint(double v_src, double r_ballast, double temp_c) const {
        double v_low = 0.0;
        double v_high = v_src;
        double v_mid = 0.0;

        for (int iter = 0; iter < 60; ++iter) {
            v_mid = 0.5 * (v_low + v_high);
            const double i_d = calculateReverseCurrent(v_mid, temp_c);
            const double v_drop = v_src - i_d * r_ballast;

            if (v_drop > v_mid) {
                v_low = v_mid;
            } else {
                v_high = v_mid;
            }
        }

        const double final_i = calculateReverseCurrent(v_mid, temp_c);
        return {v_mid, final_i};
    }

private:
    DiodeParams params_;
};

int main() {
    const DiodeParams zener5v6{5.6, 0.0001, 1e-7, 4.0, 2.0};
    const DiodeParams zener12v{12.0, 0.00085, 1e-8, 5.0, 4.5};

    const BreakdownSimulator sim5v6(zener5v6);
    const BreakdownSimulator sim12v(zener12v);

    constexpr double v_supply = 18.0;
    constexpr double r_ext = 470.0;

    std::cout << "=== Симуляція робочої точки кола стабілізації (C++) ===\n";
    std::cout << std::fixed << std::setprecision(3);

    const std::vector<double> temperatures{0.0, 25.0, 50.0, 75.0, 100.0};

    for (double temp : temperatures) {
        const auto [v5, i5] = sim5v6.solveOperatingPoint(v_supply, r_ext, temp);
        const auto [v12, i12] = sim12v.solveOperatingPoint(v_supply, r_ext, temp);

        std::cout << "T = " << std::setw(3) << static_cast<int>(temp) << " °C | "
                  << "5.6V Diod: V = " << v5 << " В, I = " << std::setw(6) << std::setprecision(2) << (i5 * 1000.0) << " мА | "
                  << "12V Diod: V = " << std::setprecision(3) << v12 << " В, I = " << std::setw(6) << std::setprecision(2) << (i12 * 1000.0) << " мА\n";
    }

    return 0;
}
