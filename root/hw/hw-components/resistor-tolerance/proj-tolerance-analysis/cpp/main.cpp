#include <iostream>
#include <vector>
#include <random>
#include <cmath>
#include <iomanip>

// Технічні параметри резистора
struct ResistorSpec {
    double nominal_ohms; // номінал в омах
    double tol_percent;  // допуск у % (1.0 для 1%)
    double tcr_ppm;      // температурний коефіцієнт у ppm/°C
};

// Звіт за результатами аналізу
struct AnalysisResult {
    double v_nominal;      // розрахункова напруга, В
    double v_min_wca;      // мінімум WCA, В
    double v_max_wca;      // максимум WCA, В
    double v_mean_mc;      // середнє за Монте-Карло, В
    double v_std_mc;       // середньоквадратичне відхилення сигма, В
    double yield_percent;  // відсоток придатних виробів, %
};

// Функція передачі дільника (чиста обчислювальна функція)
constexpr double divider_output(double v_in, double r1, double r2) noexcept {
    return v_in * r2 / (r1 + r2);
}

AnalysisResult analyze_divider(double v_in, const ResistorSpec& r1, const ResistorSpec& r2,
                              double delta_temp_c, double v_target_min, double v_target_max,
                              std::size_t mc_samples = 100'000) {
    AnalysisResult res{};
    res.v_nominal = divider_output(v_in, r1.nominal_ohms, r2.nominal_ohms);

    // 1. Повний максимальний розкид (виробничий допуск + температурний дрейф)
    const double r1_drift_pct = r1.tol_percent + (r1.tcr_ppm * delta_temp_c * 1e-4);
    const double r2_drift_pct = r2.tol_percent + (r2.tcr_ppm * delta_temp_c * 1e-4);

    const double r1_min = r1.nominal_ohms * (1.0 - r1_drift_pct * 0.01);
    const double r1_max = r1.nominal_ohms * (1.0 + r1_drift_pct * 0.01);
    const double r2_min = r2.nominal_ohms * (1.0 - r2_drift_pct * 0.01);
    const double r2_max = r2.nominal_ohms * (1.0 + r2_drift_pct * 0.01);

    // Детерміновані межі найгіршого випадку
    res.v_min_wca = divider_output(v_in, r1_max, r2_min);
    res.v_max_wca = divider_output(v_in, r1_min, r2_max);

    // 2. Симуляція Монте-Карло (генератор 64-бітний віхор Мерсенна)
    std::mt19937_64 rng(42);
    const double sigma_r1 = (r1.nominal_ohms * r1_drift_pct * 0.01) / 3.0;
    const double sigma_r2 = (r2.nominal_ohms * r2_drift_pct * 0.01) / 3.0;

    std::normal_distribution<double> dist_r1(r1.nominal_ohms, sigma_r1);
    std::normal_distribution<double> dist_r2(r2.nominal_ohms, sigma_r2);

    double sum_v = 0.0;
    double sum_v_sq = 0.0;
    std::size_t passing_count = 0;

    for (std::size_t i = 0; i < mc_samples; ++i) {
        const double sim_r1 = dist_r1(rng);
        const double sim_r2 = dist_r2(rng);
        const double sim_v = divider_output(v_in, sim_r1, sim_r2);

        sum_v += sim_v;
        sum_v_sq += sim_v * sim_v;

        if (sim_v >= v_target_min && sim_v <= v_target_max) {
            ++passing_count;
        }
    }

    res.v_mean_mc = sum_v / static_cast<double>(mc_samples);
    const double variance = (sum_v_sq / static_cast<double>(mc_samples)) - (res.v_mean_mc * res.v_mean_mc);
    res.v_std_mc = (variance > 0.0) ? std::sqrt(variance) : 0.0;
    res.yield_percent = (static_cast<double>(passing_count) / static_cast<double>(mc_samples)) * 100.0;

    return res;
}

int main() {
    constexpr double v_in = 5.0;
    const ResistorSpec r1{10000.0, 1.0, 50.0};
    const ResistorSpec r2{10000.0, 1.0, 50.0};

    const double delta_t = 50.0;
    const double v_min_spec = 2.475;
    const double v_max_spec = 2.525;

    const auto res = analyze_divider(v_in, r1, r2, delta_t, v_min_spec, v_max_spec);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "====================================================\n";
    std::cout << "   РЕЗУЛЬТАТИ ЧИСЛОВОГО АНАЛІЗУ ДІЛЬНИКА НАПРУГИ    \n";
    std::cout << "====================================================\n";
    std::cout << "Номінальна напруга:     " << res.v_nominal << " В\n";
    std::cout << "Межі Worst-Case (WCA):  " << res.v_min_wca << " В ... " << res.v_max_wca << " В\n";
    std::cout << "Монте-Карло сер. (Mean):" << res.v_mean_mc << " В\n";
    std::cout << "Відхилення сигма (Std): " << std::setprecision(5) << res.v_std_mc << " В\n";
    std::cout << "Вихід придатних (Yield):" << std::setprecision(2) << res.yield_percent << " %\n";
    std::cout << "====================================================\n";

    return 0;
}
