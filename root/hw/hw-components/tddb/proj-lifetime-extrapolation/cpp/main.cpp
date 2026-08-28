#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <iomanip>

namespace tddb {

inline constexpr double KB_EV = 8.617333262145e-5;

struct DeviceGeometry {
    double t_ox_nm{1.4};
    double a_test_cm2{1e-6};
    double a_chip_cm2{0.05};
};

struct WeibullParameters {
    double beta{1.0};
    double eta{1.0};
};

struct StressCondition {
    double voltage{0.0};
    double eta{0.0};
};

class LifetimeAnalyzer {
public:
    explicit LifetimeAnalyzer(DeviceGeometry geom) : geom_(geom) {}

    [[nodiscard]] WeibullParameters fit_weibull(std::vector<double> samples) const {
        std::sort(samples.begin(), samples.end());
        const auto n = static_cast<double>(samples.size());

        std::vector<double> x_vals;
        std::vector<double> y_vals;
        x_vals.reserve(samples.size());
        y_vals.reserve(samples.size());

        for (size_t i = 1; i <= samples.size(); ++i) {
            const double f = (static_cast<double>(i) - 0.3) / (n + 0.4);
            x_vals.push_back(std::log(samples[i - 1]));
            y_vals.push_back(std::log(-std::log(1.0 - f)));
        }

        const double sum_x = std::accumulate(x_vals.begin(), x_vals.end(), 0.0);
        const double sum_y = std::accumulate(y_vals.begin(), y_vals.end(), 0.0);
        const double sum_xx = std::inner_product(x_vals.begin(), x_vals.end(), x_vals.begin(), 0.0);
        const double sum_xy = std::inner_product(x_vals.begin(), x_vals.end(), y_vals.begin(), 0.0);

        const double slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x);
        const double intercept = (sum_y - slope * sum_x) / n;

        return WeibullParameters{
            .beta = slope,
            .eta = std::exp(-intercept / slope)
        };
    }

    [[nodiscard]] double fit_power_law(const std::vector<StressCondition>& points) const {
        const auto n = static_cast<double>(points.size());
        double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0;

        for (const auto& pt : points) {
            const double x = std::log(pt.voltage);
            const double y = std::log(pt.eta);
            sum_x += x;
            sum_y += y;
            sum_xx += x * x;
            sum_xy += x * y;
        }

        const double slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x);
        return -slope; // n_v
    }

    [[nodiscard]] double calculate_acceleration_factor(
        double v_stress, double v_op, double n_v,
        double t_stress_c, double t_op_c, double ea_ev) const {
        const double af_v = std::pow(v_stress / v_op, n_v);
        const double t_stress_k = t_stress_c + 273.15;
        const double t_op_k = t_op_c + 273.15;
        const double delta_inv_t = (1.0 / t_op_k) - (1.0 / t_stress_k);
        const double af_t = std::exp((ea_ev / KB_EV) * delta_inv_t);
        return af_v * af_t;
    }

    [[nodiscard]] double extrapolate_chip_years(
        double eta_stress, double af_total, double beta, double target_f) const {
        const double eta_op_test = eta_stress * af_total;
        const double area_scale = std::pow(geom_.a_test_cm2 / geom_.a_chip_cm2, 1.0 / beta);
        const double eta_op_chip = eta_op_test * area_scale;
        const double w_target = -std::log(1.0 - target_f);
        const double t_sec = eta_op_chip * std::pow(w_target, 1.0 / beta);
        return t_sec / (365.25 * 24.0 * 3600.0);
    }

private:
    DeviceGeometry geom_;
};

} // namespace tddb

int main() {
    using namespace tddb;

    const DeviceGeometry geom{
        .t_ox_nm = 1.4,
        .a_test_cm2 = 1e-6,
        .a_chip_cm2 = 0.05
    };
    const LifetimeAnalyzer analyzer(geom);

    const std::vector<double> samples = {
        450.2, 780.5, 920.1, 1105.4, 1340.8, 1560.2, 1780.9, 1950.0,
        2240.3, 2510.6, 2890.4, 3210.1, 3650.8, 4120.5, 4890.2
    };

    const auto [beta, eta_stress] = analyzer.fit_weibull(samples);
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Оцінений нахил Вейбула beta: " << beta << '\n';
    std::cout << "Характеристичний час стресу eta: " << eta_stress << " с\n";

    const std::vector<StressCondition> stress_points = {
        { .voltage = 2.8, .eta = 450.0 },
        { .voltage = 2.6, .eta = eta_stress },
        { .voltage = 2.4, .eta = 15400.0 }
    };
    const double n_v = analyzer.fit_power_law(stress_points);
    std::cout << "Показник напругового прискорення n_v: " << n_v << '\n';

    const double af = analyzer.calculate_acceleration_factor(2.6, 0.85, n_v, 125.0, 85.0, 0.75);
    std::cout << std::scientific << std::setprecision(2);
    std::cout << "Загальний коефіцієнт прискорення AF: " << af << '\n';

    const double years_100ppm = analyzer.extrapolate_chip_years(eta_stress, af, beta, 0.0001);
    std::cout << "Термін служби чіпа до 100 ppm браку: " << years_100ppm << " років\n";

    return 0;
}
