#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <iomanip>
#include <cmath>

namespace physics::nuclear {

/* Фізичні константи */
constexpr double AMU_TO_KG = 1.66053906660e-27;
constexpr double AMU_TO_MEV = 931.494102;
constexpr double SPEED_OF_LIGHT = 299792458.0;
constexpr double HYDROGEN1_MASS_AMU = 1.00782503207;
constexpr double NEUTRON_MASS_AMU = 1.00866491595;

struct NucleusSpec {
    std::string symbol;
    int Z{0};
    int A{0};
    double mass_amu{0.0};
};

struct BindingEnergyReport {
    double mass_defect_amu{0.0};
    double mass_defect_kg{0.0};
    double binding_energy_mev{0.0};
    double binding_energy_joules{0.0};
    double binding_energy_per_nucleon_mev{0.0};
};

struct ParticleSpec {
    std::string name;
    double mass_amu{0.0};
    int count{1};
};

struct ReactionAnalysisReport {
    double q_value_mev{0.0};
    double threshold_energy_mev{0.0};
    bool is_exothermic{true};
};

class NuclearPhysicsEngine {
public:
    static std::optional<BindingEnergyReport> compute_binding_energy(const NucleusSpec& spec) {
        if (spec.Z <= 0 || spec.A < spec.Z || spec.mass_amu <= 0.0) {
            return std::nullopt;
        }

        const int N = spec.A - spec.Z;
        const double sum_free = spec.Z * HYDROGEN1_MASS_AMU + N * NEUTRON_MASS_AMU;
        const double defect_amu = sum_free - spec.mass_amu;

        if (defect_amu < 0.0) {
            return std::nullopt;
        }

        BindingEnergyReport report;
        report.mass_defect_amu = defect_amu;
        report.mass_defect_kg = defect_amu * AMU_TO_KG;
        report.binding_energy_mev = defect_amu * AMU_TO_MEV;
        report.binding_energy_joules = report.mass_defect_kg * SPEED_OF_LIGHT * SPEED_OF_LIGHT;
        report.binding_energy_per_nucleon_mev = report.binding_energy_mev / spec.A;

        return report;
    }

    static std::optional<ReactionAnalysisReport> analyze_reaction(
        const std::vector<ParticleSpec>& reactants,
        const std::vector<ParticleSpec>& products) {
        
        if (reactants.empty() || products.empty()) {
            return std::nullopt;
        }

        double m_in = 0.0;
        for (const auto& r : reactants) {
            if (r.mass_amu <= 0.0 || r.count <= 0) return std::nullopt;
            m_in += r.mass_amu * r.count;
        }

        double m_out = 0.0;
        for (const auto& p : products) {
            if (p.mass_amu <= 0.0 || p.count <= 0) return std::nullopt;
            m_out += p.mass_amu * p.count;
        }

        const double delta_m = m_in - m_out;
        ReactionAnalysisReport report;
        report.q_value_mev = delta_m * AMU_TO_MEV;
        report.is_exothermic = (report.q_value_mev >= 0.0);

        if (!report.is_exothermic && reactants.size() >= 2) {
            const double m_proj = reactants[0].mass_amu;
            const double m_target = reactants[1].mass_amu;
            report.threshold_energy_mev = std::abs(report.q_value_mev) * (1.0 + m_proj / m_target);
        } else {
            report.threshold_energy_mev = 0.0;
        }

        return report;
    }
};

} // namespace physics::nuclear

int main() {
    using namespace physics::nuclear;

    std::cout << "=====================================================\n"
              << "  ЯДЕРНИЙ КАЛЬКУЛЯТОР ДЕФЕКТУ МАСИ ТА РЕАКЦІЙ (C++)\n"
              << "=====================================================\n\n";

    /* Аналіз ядра Урану-235 */
    NucleusSpec u235{"235U", 92, 235, 235.043930};
    auto report_u235 = NuclearPhysicsEngine::compute_binding_energy(u235);

    if (report_u235) {
        std::cout << "--- Аналіз ядра " << u235.symbol << " ---\n"
                  << std::fixed << std::setprecision(6)
                  << "  Дефект маси:   " << report_u235->mass_defect_amu << " u (" 
                  << std::scientific << report_u235->mass_defect_kg << " kg)\n"
                  << std::fixed << std::setprecision(3)
                  << "  Енергія зв'язку: " << report_u235->binding_energy_mev << " MeV (" 
                  << std::scientific << report_u235->binding_energy_joules << " J)\n"
                  << std::fixed << std::setprecision(3)
                  << "  Питома енергія:  " << report_u235->binding_energy_per_nucleon_mev << " MeV/nucleon\n\n";
    }

    /* Аналіз виходу реакції поділу урану-235: n + 235U -> 92Kr + 141Ba + 3n */
    std::vector<ParticleSpec> reactants = {
        {"Neutron (n)", 1.008665, 1},
        {"Uranium-235 (235U)", 235.043930, 1}
    };

    std::vector<ParticleSpec> products = {
        {"Krypton-92 (92Kr)", 91.926156, 1},
        {"Barium-141 (141Ba)", 140.914411, 1},
        {"Neutron (n)", 1.008665, 3}
    };

    auto reaction_report = NuclearPhysicsEngine::analyze_reaction(reactants, products);
    if (reaction_report) {
        std::cout << "--- Реакція поділу: n + 235U -> 92Kr + 141Ba + 3n ---\n"
                  << std::fixed << std::setprecision(3)
                  << "  Q-значення реакції: " << reaction_report->q_value_mev << " MeV\n";
        if (reaction_report->is_exothermic) {
            std::cout << "  Режим: Екзотермічний (виділення енергії)\n";
        } else {
            std::cout << "  Режим: Ендотермічний (поріг: " << reaction_report->threshold_energy_mev << " MeV)\n";
        }
    }

    return 0;
}
