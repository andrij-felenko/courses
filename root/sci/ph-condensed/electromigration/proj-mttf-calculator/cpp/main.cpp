#include <iostream>
#include <cmath>
#include <optional>
#include <string_view>

namespace physics::electromigration {

constexpr double kBoltzmannEv = 8.617333262145e-5; // еВ/К

struct MetalProcess {
    double activation_energy_ev{0.9};
    double current_exponent{1.5};
    double blech_product_a_cm{3500.0};
};

struct StressCondition {
    double temp_celsius{25.0};
    double current_density_a_cm2{1.0e5};

    [[nodiscard]] constexpr double temp_kelvin() const noexcept {
        return temp_celsius + 273.15;
    }
};

struct ReliabilityReport {
    double acceleration_factor{1.0};
    double mttf_use_hours{0.0};
    double critical_length_um{0.0};
    bool is_blech_immune{false};

    [[nodiscard]] constexpr double mttf_years() const noexcept {
        return mttf_use_hours / 8760.0;
    }
};

class ElectromigrationEvaluator {
public:
    explicit constexpr ElectromigrationEvaluator(MetalProcess process) noexcept
        : process_(process) {}

    [[nodiscard]] std::optional<ReliabilityReport> evaluate(
        const StressCondition& test_cond,
        double mttf_test_hours,
        const StressCondition& use_cond,
        double line_length_um
    ) const noexcept {
        if (test_cond.current_density_a_cm2 <= 0.0 || use_cond.current_density_a_cm2 <= 0.0) {
            return std::nullopt;
        }

        const double current_ratio = test_cond.current_density_a_cm2 / use_cond.current_density_a_cm2;
        const double j_factor = std::pow(current_ratio, process_.current_exponent);

        const double temp_diff_inv = (1.0 / use_cond.temp_kelvin()) - (1.0 / test_cond.temp_kelvin());
        const double t_factor = std::exp((process_.activation_energy_ev / kBoltzmannEv) * temp_diff_inv);

        ReliabilityReport report{};
        report.acceleration_factor = j_factor * t_factor;
        report.mttf_use_hours = mttf_test_hours * report.acceleration_factor;
        report.critical_length_um = (process_.blech_product_a_cm / use_cond.current_density_a_cm2) * 1.0e4;
        report.is_blech_immune = (line_length_um <= report.critical_length_um);

        return report;
    }

private:
    MetalProcess process_;
};

} // namespace physics::electromigration

int main() {
    using namespace physics::electromigration;

    constexpr MetalProcess cu_process{
        .activation_energy_ev = 0.90,
        .current_exponent = 1.5,
        .blech_product_a_cm = 3500.0
    };

    const StressCondition htol_test{.temp_celsius = 200.0, .current_density_a_cm2 = 3.0e6};
    const StressCondition operational_use{.temp_celsius = 105.0, .current_density_a_cm2 = 5.0e5};
    const double mttf_test_h = 120.0;
    const double line_length_um = 50.0;

    ElectromigrationEvaluator evaluator(cu_process);
    auto result = evaluator.evaluate(htol_test, mttf_test_h, operational_use, line_length_um);

    if (result.has_value()) {
        std::cout << "=== C++17 Результати аналізу електроміграційної надійності ===\n";
        std::cout << "Коефіцієнт прискорення (AF): " << result->acceleration_factor << "\n";
        std::cout << "Прогнозований MTTF: " << result->mttf_use_hours << " годин ("
                  << result->mttf_years() << " років)\n";
        std::cout << "Критична довжина Блеха: " << result->critical_length_um << " мкм\n";
        std::cout << "Статус імунітету Блеха (L=" << line_length_um << " мкм): "
                  << (result->is_blech_immune ? "БЕЗСМЕРТНА LINE" : "ОБМЕЖЕНА ЕЛЕКТРОМІГРАЦІЄЮ") << "\n";
    }

    return 0;
}
