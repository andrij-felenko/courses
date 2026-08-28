#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <cmath>
#include <random>
#include <numeric>
#include <algorithm>

struct Component {
    std::string name;
    double nom;      // Номінальне значення
    double tol_pct;  // Повний допуск життєвого циклу (%)
};

class CircuitAnalyzer {
public:
    static constexpr double calc_vout(double vin, double r1, double r2) noexcept {
        return vin * (1.0 + r2 / r1);
    }

    struct WccaResult {
        double v_nom;
        double s_rel_vin, s_rel_r1, s_rel_r2;
        double eva_min, eva_max;
        double rss_tol_pct, rss_min, rss_max;
        double mc_mean, mc_stddev;
        double mc_min, mc_max;
        double yield_pct;
        int defect_ppm;
    };

    static WccaResult run_full_analysis(const Component& vin,
                                        const Component& r1,
                                        const Component& r2,
                                        double spec_low,
                                        double spec_high,
                                        std::size_t mc_iterations = 100'000) {
        WccaResult res{};
        res.v_nom = calc_vout(vin.nom, r1.nom, r2.nom);

        // 1. Чутливості
        const double sens_vin = 1.0 + r2.nom / r1.nom;
        const double sens_r2  = vin.nom / r1.nom;
        const double sens_r1  = -vin.nom * r2.nom / (r1.nom * r1.nom);

        res.s_rel_vin = (vin.nom / res.v_nom) * sens_vin;
        res.s_rel_r2  = (r2.nom / res.v_nom) * sens_r2;
        res.s_rel_r1  = (r1.nom / res.v_nom) * sens_r1;

        // 2. EVA Worst-Case
        const double vin_min = vin.nom * (1.0 - vin.tol_pct / 100.0);
        const double vin_max = vin.nom * (1.0 + vin.tol_pct / 100.0);
        const double r1_min  = r1.nom * (1.0 - r1.tol_pct / 100.0);
        const double r1_max  = r1.nom * (1.0 + r1.tol_pct / 100.0);
        const double r2_min  = r2.nom * (1.0 - r2.tol_pct / 100.0);
        const double r2_max  = r2.nom * (1.0 + r2.tol_pct / 100.0);

        res.eva_min = calc_vout(vin_min, r1_max, r2_min);
        res.eva_max = calc_vout(vin_max, r1_min, r2_max);

        // 3. RSS 3-Sigma
        const double var_sum = std::pow(res.s_rel_vin * vin.tol_pct, 2) +
                               std::pow(res.s_rel_r1  * r1.tol_pct, 2) +
                               std::pow(res.s_rel_r2  * r2.tol_pct, 2);
        res.rss_tol_pct = std::sqrt(var_sum);
        res.rss_min = res.v_nom * (1.0 - res.rss_tol_pct / 100.0);
        res.rss_max = res.v_nom * (1.0 + res.rss_tol_pct / 100.0);

        // 4. Monte Carlo Simulation
        std::mt19937_64 rng{12345};
        std::normal_distribution<double> dist_vin(vin.nom, (vin.nom * (vin.tol_pct / 100.0)) / 3.0);
        std::normal_distribution<double> dist_r1(r1.nom,   (r1.nom * (r1.tol_pct / 100.0)) / 3.0);
        std::normal_distribution<double> dist_r2(r2.nom,   (r2.nom * (r2.tol_pct / 100.0)) / 3.0);

        std::vector<double> samples;
        samples.reserve(mc_iterations);

        std::size_t out_of_spec_count = 0;
        double sum = 0.0;

        for (std::size_t i = 0; i < mc_iterations; ++i) {
            const double v_sample = calc_vout(dist_vin(rng), dist_r1(rng), dist_r2(rng));
            samples.push_back(v_sample);
            sum += v_sample;
            if (v_sample < spec_low || v_sample > spec_high) {
                ++out_of_spec_count;
            }
        }

        res.mc_mean = sum / static_cast<double>(mc_iterations);

        double sq_diff_sum = 0.0;
        for (double s : samples) {
            sq_diff_sum += (s - res.mc_mean) * (s - res.mc_mean);
        }
        res.mc_stddev = std::sqrt(sq_diff_sum / static_cast<double>(mc_iterations));

        auto [min_it, max_it] = std::minmax_element(samples.begin(), samples.end());
        res.mc_min = *min_it;
        res.mc_max = *max_it;

        res.yield_pct = 100.0 * (1.0 - (static_cast<double>(out_of_spec_count) / mc_iterations));
        res.defect_ppm = static_cast<int>((static_cast<double>(out_of_spec_count) / mc_iterations) * 1'000'000.0);

        return res;
    }
};

int main() {
    const Component vin_src{"Vin", 1.000, 0.50};
    const Component r1_res {"R1",  10000.0, 3.00};
    const Component r2_res {"R2",  90000.0, 3.00};

    constexpr double spec_low = 9.60;
    constexpr double spec_high = 10.40;

    const auto res = CircuitAnalyzer::run_full_analysis(vin_src, r1_res, r2_res, spec_low, spec_high);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== РЕЗУЛЬТАТИ АНАЛІЗУ НАЙГІРШОГО ВИПАДКУ (C++20 WCCA) ===\n";
    std::cout << "Номінальний вихід Vout: " << res.v_nom << " В\n\n";

    std::cout << "1. Аналіз чутливості (Sensitivity):\n";
    std::cout << "   S_rel(Vin) = " << std::showpos << res.s_rel_vin << "\n";
    std::cout << "   S_rel(R1)  = " << res.s_rel_r1 << "\n";
    std::cout << "   S_rel(R2)  = " << res.s_rel_r2 << "\n\n" << std::noshowpos;

    std::cout << "2. Метод граничних значень (EVA Worst-Case):\n";
    std::cout << "   Vout_min = " << res.eva_min << " В (" << (100.0 * (res.eva_min - res.v_nom) / res.v_nom) << "%)\n";
    std::cout << "   Vout_max = " << res.eva_max << " В (" << (100.0 * (res.eva_max - res.v_nom) / res.v_nom) << "%)\n";
    std::cout << "   Сумарне вікно розкиду EVA: " << (res.eva_max - res.eva_min) << " В\n\n";

    std::cout << "3. Метод Root-Sum-Square (RSS 3-Sigma):\n";
    std::cout << "   Статистичний допуск: +-" << std::setprecision(2) << res.rss_tol_pct << "%\n" << std::setprecision(4);
    std::cout << "   Vout_min (3-Sigma) = " << res.rss_min << " В\n";
    std::cout << "   Vout_max (3-Sigma) = " << res.rss_max << " В\n\n";

    std::cout << "4. Статистичне моделювання Монте-Карло (100 000 прогонів):\n";
    std::cout << "   Середнє значення mu:   " << res.mc_mean << " В\n";
    std::cout << "   Стандартне відхилення: " << res.mc_stddev << " В\n";
    std::cout << "   Діапазон вибірки:      [" << res.mc_min << " В ... " << res.mc_max << " В]\n";
    std::cout << "   Вихід придатних:       " << std::setprecision(3) << res.yield_pct << "% (Брак: " << res.defect_ppm << " PPM)\n";

    return 0;
}
