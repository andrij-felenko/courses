#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <span>
#include <optional>

namespace PowerEfficiency {

struct DcSource {
    double emf_v{12.0};
    double internal_r{2.0};
};

struct EfficiencyPoint {
    double r_load_ohm{0.0};
    double ratio_r{0.0};
    double current_amp{0.0};
    double p_useful_watt{0.0};
    double p_loss_watt{0.0};
    double efficiency{0.0};
};

struct TransformerSpec {
    double nominal_kva{1000.0};
    double p_core_kw{2.5};
    double p_copper_kw{10.0};
    double power_factor{0.90};
};

class CircuitAnalyzer {
public:
    static std::vector<EfficiencyPoint> sweepLoad(const DcSource& source, 
                                                 double r_start, 
                                                 double r_end, 
                                                 std::size_t steps) {
        if (steps == 0 || source.internal_r <= 0.0) {
            return {};
        }

        std::vector<EfficiencyPoint> results;
        results.reserve(steps);

        const double step_size = (r_end - r_start) / static_cast<double>(steps > 1 ? steps - 1 : 1);

        for (std::size_t i = 0; i < steps; ++i) {
            const double r_l = r_start + static_cast<double>(i) * step_size;
            const double total_r = r_l + source.internal_r;
            const double current = source.emf_v / total_r;
            const double p_useful = current * current * r_l;
            const double p_loss = current * current * source.internal_r;
            const double eta = p_useful / (p_useful + p_loss);

            results.push_back(EfficiencyPoint{
                .r_load_ohm = r_l,
                .ratio_r = r_l / source.internal_r,
                .current_amp = current,
                .p_useful_watt = p_useful,
                .p_loss_watt = p_loss,
                .efficiency = eta
            });
        }
        return results;
    }
};

class TransformerOptimizer {
public:
    explicit TransformerOptimizer(TransformerSpec spec) : spec_(spec) {}

    [[nodiscard]] std::optional<double> calculateOptimalK() const noexcept {
        if (spec_.p_copper_kw <= 0.0 || spec_.p_core_kw <= 0.0) {
            return std::nullopt;
        }
        return std::sqrt(spec_.p_core_kw / spec_.p_copper_kw);
    }

    [[nodiscard]] double calculateEfficiency(double load_factor_k) const noexcept {
        if (load_factor_k < 0.0) return 0.0;
        const double p_out = load_factor_k * spec_.nominal_kva * spec_.power_factor;
        const double p_losses = spec_.p_core_kw + (load_factor_k * load_factor_k) * spec_.p_copper_kw;
        if (p_out + p_losses <= 0.0) return 0.0;
        return p_out / (p_out + p_losses);
    }

private:
    TransformerSpec spec_;
};

} // namespace PowerEfficiency

int main() {
    using namespace PowerEfficiency;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== СИМУЛЯТОР ККД ТА ЕНЕРГЕТИЧНОГО БАЛАНСУ (C++20) ===\n\n";

    const DcSource source{.emf_v = 24.0, .internal_r = 1.5};
    auto analysis = CircuitAnalyzer::sweepLoad(source, 0.5, 7.5, 5);

    std::cout << "--- Аналіз джерела (ЕРС = 24В, r = 1.5 Ом) ---\n";
    std::cout << "R_L (Ом) | R_L/r | Струм (А) | P_кор (Вт) | P_вт (Вт) | ККД (%)\n";
    std::cout << "----------------------------------------------------------\n";
    for (const auto& pt : analysis) {
        std::cout << std::setw(7) << pt.r_load_ohm << "  | "
                  << std::setw(5) << pt.ratio_r << " | "
                  << std::setw(9) << pt.current_amp << " | "
                  << std::setw(10) << pt.p_useful_watt << " | "
                  << std::setw(9) << pt.p_loss_watt << " | "
                  << std::setw(6) << pt.efficiency * 100.0 << "%\n";
    }

    const TransformerSpec trans_spec{
        .nominal_kva = 2500.0,
        .p_core_kw = 4.0,
        .p_copper_kw = 16.0,
        .power_factor = 0.95
    };

    TransformerOptimizer optimizer(trans_spec);
    if (auto opt_k = optimizer.calculateOptimalK()) {
        std::cout << "\n--- Оптимізація трансформатора " << trans_spec.nominal_kva << " кВА ---\n";
        std::cout << "Оптимальний коефіцієнт k_opt: " << *opt_k << " (" << (*opt_k * 100.0) << "% від номіналу)\n";
        std::cout << "Максимальний ККД: " << (optimizer.calculateEfficiency(*opt_k) * 100.0) << "%\n";
        std::cout << "Номінальний ККД (k=1.0): " << (optimizer.calculateEfficiency(1.0) * 100.0) << "%\n";
    }

    return 0;
}
