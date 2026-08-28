#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <string_view>
#include <iomanip>
#include <algorithm>

/* Опис групи конденсаторів однакового номіналу та типорозміру */
struct CapacitorGroup {
    std::string_view name;
    double capacitance_f;   // Ефективна ємність (Ф)
    double esr_ohm;         // Власний еквівалентний послідовний опір (Ом)
    double esl_henry;       // Власна індуктивність корпусу (Гн)
    double via_inductance_h;// Індуктивність перехідних отворів (Гн)
    double trace_resistance_ohm; // Активний опір друкованої траси (Ом)
    int count;              // Кількість паралельних компонентів

    [[nodiscard]] std::complex<double> branch_impedance(double omega) const noexcept {
        const double r_total = esr_ohm + trace_resistance_ohm;
        const double l_total = esl_henry + via_inductance_h;
        const double x_reactance = omega * l_total - 1.0 / (omega * capacitance_f);
        return {r_total, x_reactance};
    }
};

/* Клас аналізу та оптимізації розподільчої мережі живлення */
class PdnAnalyzer {
public:
    explicit PdnAnalyzer(double target_impedance_ohm) noexcept
        : target_impedance_{target_impedance_ohm} {}

    [[nodiscard]] std::complex<double> calculate_impedance(
        std::span<const CapacitorGroup> groups, double frequency_hz) const noexcept {
        
        const double omega = 2.0 * std::numbers::pi * frequency_hz;
        std::complex<double> y_total{0.0, 0.0};

        for (const auto& grp : groups) {
            if (grp.count <= 0 || grp.capacitance_f <= 0.0) continue;
            const auto z_branch = grp.branch_impedance(omega);
            y_total += static_cast<double>(grp.count) / z_branch;
        }

        if (std::abs(y_total) == 0.0) return {1e9, 0.0};
        return 1.0 / y_total;
    }

    void run_sweep(std::span<const CapacitorGroup> groups,
                   double start_freq_hz, double stop_freq_hz,
                   int points_per_decade) const {
        
        std::cout << "========================================================================\n"
                  << "           СИМУЛЯЦІЯ ІМПЕДАНСНОГО ПРОФІЛЮ ШИНИ ЖИВЛЕННЯ (PDN)           \n"
                  << "========================================================================\n"
                  << "Цільовий імпеданс Z_target: " << target_impedance_ * 1000.0 << " мОм\n\n"
                  << std::left << std::setw(12) << "Частота" << " | "
                  << std::setw(12) << "|Z_PDN| (мОм)" << " | "
                  << std::setw(10) << "Фаза (°)" << " | "
                  << "Статус\n"
                  << "-------------+--------------+------------+-----------\n";

        const double step_factor = std::pow(10.0, 1.0 / static_cast<double>(points_per_decade));
        double current_freq = start_freq_hz;
        double peak_impedance = 0.0;
        double peak_frequency = 0.0;
        std::size_t violation_count = 0;
        int point_idx = 0;

        while (current_freq <= stop_freq_hz) {
            const auto z_pdn = calculate_impedance(groups, current_freq);
            const double magnitude = std::abs(z_pdn);
            const double phase_deg = std::arg(z_pdn) * (180.0 / std::numbers::pi);
            const bool is_violation = (magnitude > target_impedance_);

            if (is_violation) violation_count++;
            if (magnitude > peak_impedance) {
                peak_impedance = magnitude;
                peak_frequency = current_freq;
            }

            if (point_idx % (points_per_decade / 2) == 0 || is_violation) {
                std::string unit = "Гц";
                double disp_freq = current_freq;
                if (current_freq >= 1e6) { disp_freq /= 1e6; unit = "МГц"; }
                else if (current_freq >= 1e3) { disp_freq /= 1e3; unit = "кГц"; }

                std::cout << std::right << std::setw(7) << std::fixed << std::setprecision(2) << disp_freq
                          << " " << std::left << std::setw(4) << unit << " | "
                          << std::right << std::setw(10) << std::setprecision(3) << magnitude * 1000.0 << "   | "
                          << std::setw(8) << std::setprecision(1) << phase_deg << "°  | "
                          << (is_violation ? "УВАГА: ПІК!" : "НОРМА") << "\n";
            }

            current_freq *= step_factor;
            point_idx++;
        }

        std::cout << "------------------------------------------------------------------------\n"
                  << "Максимальний імпеданс: " << peak_impedance * 1000.0 << " мОм на частоті "
                  << peak_frequency / 1e6 << " МГц\n";

        if (violation_count > 0) {
            std::cout << "ВИСНОВОК: Виявлено " << violation_count 
                      << " точок перевищення Z_target! Потрібна оптимізація демпфування.\n";
        } else {
            std::cout << "ВИСНОВОК: Імпеданс шини живлення відповідає цільовим вимогам.\n";
        }
        std::cout << "========================================================================\n\n";
    }

private:
    double target_impedance_;
};

int main() {
    constexpr double z_target_fpga = 0.0018; // 1.8 мОм

    const std::vector<CapacitorGroup> pdn_stack = {
        {"Bulk Al-Polymer 470uF", 470e-6,  0.010, 2.5e-9, 0.8e-9, 0.001,  4},
        {"MLCC 0805 X7R 22uF",    15.0e-6, 0.008, 0.8e-9, 0.5e-9, 0.0005, 10},
        {"MLCC 0402 X7R 1uF",     0.7e-6,  0.012, 0.4e-9, 0.3e-9, 0.0005, 20},
        {"MLCC 0201 X7R 100nF",   0.08e-6, 0.018, 0.2e-9, 0.2e-9, 0.0005, 40}
    };

    const PdnAnalyzer analyzer{z_target_fpga};
    analyzer.run_sweep(pdn_stack, 10e3, 500e6, 20);

    return 0;
}
