#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>

struct Segment {
    std::string name;
    double length;          // L (м)
    double diameter;        // d (м)
    double young_modulus;   // E (Па)
    double poisson_ratio;   // ν
    double alpha{0.0};      // α (1/K)
    double delta_t{0.0};    // ΔT (K)
};

struct SegmentResult {
    std::string name;
    double stress_MPa;
    double strain_mech_pct;
    double delta_l_mm;
    double delta_d_um;
    double energy_J;
};

class RodSimulator {
public:
    explicit RodSimulator(double axial_force) : force_(axial_force) {}

    SegmentResult simulate_segment(const Segment& seg) const {
        const double area = M_PI * std::pow(seg.diameter, 2) / 4.0;
        const double stress = force_ / area;
        const double strain_mech = stress / seg.young_modulus;
        const double strain_therm = seg.alpha * seg.delta_t;
        const double strain_total = strain_mech + strain_therm;

        const double delta_l = seg.length * strain_total;
        const double delta_d = -seg.poisson_ratio * strain_mech * seg.diameter;
        const double volume = area * seg.length;
        const double energy = 0.5 * stress * strain_mech * volume;

        return SegmentResult{
            seg.name,
            stress / 1e6,
            strain_mech * 100.0,
            delta_l * 1000.0,
            delta_d * 1e6,
            energy
        };
    }

private:
    double force_;
};

int main() {
    const std::vector<Segment> rod = {
        {"Сталевий сегмент", 0.5, 0.02, 210e9, 0.30},
        {"Алюмінієвий сегмент", 0.3, 0.025, 70e9, 0.33}
    };
    const double force = 50000.0; // 50 кН

    RodSimulator sim(force);
    double total_delta_l_mm = 0.0;
    double total_energy_J = 0.0;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Результати розрахунку (C++) ===\n";

    for (const auto& seg : rod) {
        const auto res = sim.simulate_segment(seg);
        std::cout << "[" << res.name << "]\n";
        std::cout << "  Напруження σ:       " << res.stress_MPa << " МПа\n";
        std::cout << "  Пружна деформація: " << res.strain_mech_pct << " %\n";
        std::cout << "  Подовження ΔL:      " << res.delta_l_mm << " мм\n";
        std::cout << "  Зміна діаметра Δd: " << res.delta_d_um << " мкм\n";
        std::cout << "  Енергія U:          " << res.energy_J << " Дж\n\n";

        total_delta_l_mm += res.delta_l_mm;
        total_energy_J += res.energy_J;
    }

    std::cout << "Загальне подовження стержня: " << total_delta_l_mm << " мм\n";
    std::cout << "Повна потенціальна енергія:   " << total_energy_J << " Дж\n";

    return 0;
}
