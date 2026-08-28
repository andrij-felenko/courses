#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

class DnaFragment {
public:
    int length_bp;
    double position_mm{0.0};
    double mobility{0.0};

    explicit DnaFragment(int bp, double gel_conc) : length_bp(bp) {
        constexpr double v0 = 3.5e-4; // Базова рухливість (см² / (В · с))
        double k_retard = 0.045 * gel_conc;
        mobility = v0 * std::exp(-k_retard * std::sqrt(static_cast<double>(bp)));
    }
};

class GelElectrophoresisSim {
private:
    double length_mm_{100.0};
    double gel_concentration_{1.0};
    double field_v_cm_{5.0};
    double temp_c_{22.0};
    double ambient_temp_c_{22.0};
    double conductivity_{0.15};
    std::vector<DnaFragment> fragments_;

public:
    GelElectrophoresisSim(double gel_conc, double field_v_cm, const std::vector<int>& bp_sizes)
        : gel_concentration_(gel_conc), field_v_cm_(field_v_cm) {
        fragments_.reserve(bp_sizes.size());
        for (int bp : bp_sizes) {
            fragments_.emplace_back(bp, gel_conc);
        }
    }

    void Step(double dt_sec) {
        // Гідродинамічне переміщення смуг
        double temp_factor = 1.0 + 0.02 * (temp_c_ - 25.0);
        for (auto& frag : fragments_) {
            double current_v = frag.mobility * field_v_cm_ * temp_factor;
            frag.position_mm += current_v * 10.0 * dt_sec; // см/с -> мм/с
        }

        // Теплова динаміка джоулевого нагріву
        double field_v_m = field_v_cm_ * 100.0;
        double joule_power_m3 = conductivity_ * field_v_m * field_v_m;
        constexpr double heat_capacity = 4184.0;
        constexpr double density = 1000.0;
        constexpr double cooling_coeff = 0.05;

        double dT_dt = (joule_power_m3 / (density * heat_capacity)) - 
                       cooling_coeff * (temp_c_ - ambient_temp_c_);
        temp_c_ += dT_dt * dt_sec;
    }

    void PrintState(double current_time_sec) const {
        std::cout << "Час: " << std::setw(4) << current_time_sec 
                  << " с | Температура гелю: " << std::fixed << std::setprecision(2) 
                  << temp_c_ << " °C\n";
        for (const auto& frag : fragments_) {
            std::cout << "  Фрагмент " << std::setw(4) << frag.length_bp 
                      << " п.н. -> Зсув: " << std::setw(5) << std::setprecision(2) 
                      << frag.position_mm << " мм\n";
        }
        std::cout << "----------------------------------------\n";
    }

    [[nodiscard]] double temp_c() const { return temp_c_; }
};

int main() {
    std::cout << "=== Симуляція гелевого електрофорезу (C++) ===\n\n";

    std::vector<int> dna_ladder = {1000, 500, 200, 100};
    GelElectrophoresisSim sim(1.0, 5.0, dna_ladder);

    constexpr double dt = 10.0;
    constexpr double total_time = 1800.0;

    for (double t = 0; t <= total_time; t += dt) {
        if (static_cast<int>(t) % 600 == 0) {
            sim.PrintState(t);
        }
        sim.Step(dt);
    }

    return 0;
}
