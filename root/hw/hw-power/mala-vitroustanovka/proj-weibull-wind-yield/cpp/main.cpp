#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>

struct WindTurbine {
    double rated_power_w{1000.0};
    double v_cut_in{3.0};
    double v_rated{11.0};
    double v_cut_out{24.0};
    double rotor_radius_m{1.4};
    double cp_max{0.42};
    double eta_gen{0.85};

    [[nodiscard]] constexpr double swept_area() const noexcept {
        return std::numbers::pi * rotor_radius_m * rotor_radius_m;
    }
};

struct WindClimate {
    double shape_k{2.05};
    double scale_c{6.20};
    double air_density{1.225};

    [[nodiscard]] double pdf(double v) const noexcept {
        if (v <= 0.0 || scale_c <= 0.0 || shape_k <= 0.0) {
            return 0.0;
        }
        const double v_c = v / scale_c;
        return (shape_k / scale_c) * std::pow(v_c, shape_k - 1.0) * std::exp(-std::pow(v_c, shape_k));
    }
};

struct YieldResult {
    double aep_kwh{0.0};
    double avg_power_w{0.0};
    double capacity_factor{0.0};
    double hours_operating{0.0};
};

class WindEnergyEstimator {
public:
    static double electrical_power(const WindTurbine& t, const WindClimate& w, double v) noexcept {
        if (v < t.v_cut_in || v > t.v_cut_out) {
            return 0.0;
        }
        if (v >= t.v_rated) {
            return t.rated_power_w;
        }
        const double p_aero = 0.5 * w.air_density * t.swept_area() * std::pow(v, 3.0) * t.cp_max * t.eta_gen;
        return std::min(p_aero, t.rated_power_w);
    }

    static YieldResult evaluate(const WindTurbine& t, const WindClimate& w) noexcept {
        constexpr double v_max = 35.0;
        constexpr int steps = 1400;
        constexpr double dv = v_max / static_cast<double>(steps);
        constexpr double hours_per_year = 8760.0;

        double sum_power_weighted = 0.0;
        double sum_prob_operating = 0.0;

        for (int i = 0; i <= steps; ++i) {
            const double v = static_cast<double>(i) * dv;
            const double pdf = w.pdf(v);
            const double p_el = electrical_power(t, w, v);

            const double weight = (i == 0 || i == steps) ? 0.5 : 1.0;
            sum_power_weighted += weight * (p_el * pdf);

            if (v >= t.v_cut_in && v <= t.v_cut_out) {
                sum_prob_operating += weight * pdf;
            }
        }

        const double avg_power = sum_power_weighted * dv;
        const double aep_wh = avg_power * hours_per_year;
        const double prob_oper = sum_prob_operating * dv;

        return YieldResult{
            .aep_kwh = aep_wh / 1000.0,
            .avg_power_w = avg_power,
            .capacity_factor = avg_power / t.rated_power_w,
            .hours_operating = prob_oper * hours_per_year
        };
    }
};

int main() {
    const WindTurbine turbine;
    const WindClimate climate;

    const YieldResult res = WindEnergyEstimator::evaluate(turbine, climate);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Розрахунок річної генерації малої вітроустановки ===\n";
    std::cout << "Номінальна потужність:      " << turbine.rated_power_w << " Вт\n";
    std::cout << "Діаметр ротора:             " << (turbine.rotor_radius_m * 2.0)
              << " м (площа: " << turbine.swept_area() << " м2)\n";
    std::cout << "Параметри вітру Вейбулла:   k = " << climate.shape_k
              << ", c = " << climate.scale_c << " м/с\n";
    std::cout << "Густина повітря:            " << climate.air_density << " кг/м3\n";
    std::cout << "----------------------------------------------------\n";
    std::cout << "Середньорічна потужність:   " << std::setprecision(1) << res.avg_power_w << " Вт\n";
    std::cout << "Річна генерація (AEP):      " << res.aep_kwh << " кВт·год/рік\n";
    std::cout << "Коефіцієнт потужності (CF): " << std::setprecision(2) << (res.capacity_factor * 100.0) << " % (КВВП)\n";
    std::cout << "Час активної генерації:     " << std::setprecision(0) << res.hours_operating
              << " годин/рік (" << std::setprecision(1) << (res.hours_operating / 8760.0 * 100.0) << " % часу)\n";

    return 0;
}
