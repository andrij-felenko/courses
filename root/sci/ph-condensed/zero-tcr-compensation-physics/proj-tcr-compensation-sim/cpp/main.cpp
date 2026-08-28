#include <iostream>
#include <vector>
#include <cmath>
#include <span>
#include <optional>
#include <iomanip>

struct AlloyProperties {
    double r20{0.001};       // Опір при 20 °C, Ом
    double alpha20{2e-6};    // Лінійний ТКО, 1/К
    double beta{-4e-7};      // Квадратичний ТКО, 1/К²
    double r_th{15.0};       // Тепловий опір, К/Вт
    double t_ambient{25.0};  // Температура довкілля, °C

    [[nodiscard]] double calculate_resistance(double temp_c) const noexcept {
        const double dt = temp_c - 20.0;
        return r20 * (1.0 + alpha20 * dt + beta * dt * dt);
    }

    [[nodiscard]] double simulate_equilibrium_temp(double current_a) const noexcept {
        double temp = t_ambient;
        for (int iter = 0; iter < 10; ++iter) {
            const double r_curr = calculate_resistance(temp);
            const double power_w = current_a * current_a * r_curr;
            const double new_temp = t_ambient + power_w * r_th;
            if (std::abs(new_temp - temp) < 1e-6) {
                break;
            }
            temp = new_temp;
        }
        return temp;
    }
};

struct PolynomialFitResult {
    double r20{0.0};
    double alpha20{0.0};
    double beta{0.0};
    double t_peak{0.0};
};

class TcrAnalyzer {
public:
    [[nodiscard]] static std::optional<PolynomialFitResult> fit_parabola(
        std::span<const double> temps,
        std::span<const double> resistances) noexcept 
    {
        if (temps.size() != resistances.size() || temps.size() < 3) {
            return std::nullopt;
        }

        double s0 = static_cast<double>(temps.size()), s1 = 0, s2 = 0, s3 = 0, s4 = 0;
        double y0 = 0, y1 = 0, y2 = 0;

        for (size_t i = 0; i < temps.size(); ++i) {
            const double x = temps[i] - 20.0;
            const double x2 = x * x;
            const double y = resistances[i];

            s1 += x;
            s2 += x2;
            s3 += x2 * x;
            s4 += x2 * x2;

            y0 += y;
            y1 += y * x;
            y2 += y * x2;
        }

        const double det = s0 * (s2 * s4 - s3 * s3) - s1 * (s1 * s4 - s2 * s3) + s2 * (s1 * s3 - s2 * s2);
        if (std::abs(det) < 1e-15) {
            return std::nullopt;
        }

        const double det_a0 = y0 * (s2 * s4 - s3 * s3) - s1 * (y1 * s4 - s3 * y2) + s2 * (y1 * s3 - s2 * y2);
        const double det_a1 = s0 * (y1 * s4 - s3 * y2) - y0 * (s1 * s4 - s2 * s3) + s2 * (s1 * y2 - y1 * s2);
        const double det_a2 = s0 * (s2 * y2 - y1 * s3) - s1 * (s1 * y2 - y1 * s2) + y0 * (s1 * s3 - s2 * s2);

        const double a0 = det_a0 / det;
        const double a1 = det_a1 / det;
        const double a2 = det_a2 / det;

        PolynomialFitResult res;
        res.r20 = a0;
        res.alpha20 = a1 / a0;
        res.beta = a2 / a0;
        res.t_peak = 20.0 - (res.alpha20 / (2.0 * res.beta));

        return res;
    }
};

int main() {
    const AlloyProperties manganin{.r20 = 0.001, .alpha20 = 2e-6, .beta = -4e-7, .r_th = 15.0, .t_ambient = 25.0};

    std::cout << "=== Симуляція манганінового шунта (C++) ===\n";
    const double current = 50.0;
    const double t_eq = manganin.simulate_equilibrium_temp(current);
    const double r_eq = manganin.calculate_resistance(t_eq);
    const double dr_ppm = (r_eq - manganin.r20) / manganin.r20 * 1e6;

    std::cout << std::fixed << std::setprecision(7);
    std::cout << "Струм: " << current << " А -> Т_рівн: " << t_eq << " °C, R: " << r_eq 
              << " Ом (Зсув: " << dr_ppm << " ppm)\n\n";

    const std::vector<double> test_temps{0.0, 15.0, 25.0, 40.0, 60.0};
    std::vector<double> test_res;
    test_res.reserve(test_temps.size());

    for (double t : test_temps) {
        test_res.push_back(manganin.calculate_resistance(t));
    }

    if (auto fit = TcrAnalyzer::fit_parabola(test_temps, test_res)) {
        std::cout << "=== Результати МНК-фітингу (C++) ===\n";
        std::cout << "R20: " << fit->r20 << " Ом\n";
        std::cout << "Alpha20: " << fit->alpha20 * 1e6 << " ppm/K\n";
        std::cout << "Beta: " << fit->beta * 1e6 << " ppm/K²\n";
        std::cout << "Вершина параболи (T_peak): " << fit->t_peak << " °C\n";
    }

    return 0;
}
