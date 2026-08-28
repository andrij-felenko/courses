#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string>

namespace QcdSim {
    constexpr double ALPHA_S = 0.35;            // Константа сильного зв'язку
    constexpr double K_STRING = 1.0;            // Натяг струни K (GeV/fm)
    constexpr double MASS_QUARK = 0.35;         // Ефективна маса кварка (GeV)
    constexpr double THRESHOLD_PAIR = 2.0 * MASS_QUARK; // Поріг народження пари (GeV)

    struct State {
        double r_fm{0.0};
        double v_coulomb{0.0};
        double v_string{0.0};
        double v_total{0.0};
        double prob_break{0.0};
        bool is_broken{false};
    };

    class CornellPotentialModel {
    public:
        static double computePotential(double r_fm, double& v_coulomb, double& v_string) {
            if (r_fm <= 0.0) return 0.0;
            v_coulomb = -(4.0 / 3.0) * (ALPHA_S / r_fm);
            v_string = K_STRING * r_fm;
            return v_coulomb + v_string;
        }

        static double computeBreakingProbability(double v_total) {
            if (v_total < THRESHOLD_PAIR) return 0.0;
            double delta_e = v_total - THRESHOLD_PAIR;
            constexpr double rate = 0.85;
            return 1.0 - std::exp(-rate * delta_e);
        }

        std::vector<State> simulate(double r_start, double r_end, int steps) const {
            std::vector<State> trajectory;
            trajectory.reserve(steps);
            const double dr = (r_end - r_start) / (steps - 1);

            bool broken = false;
            for (int i = 0; i < steps; ++i) {
                double r = r_start + i * dr;
                State st;
                st.r_fm = r;
                st.v_total = computePotential(r, st.v_coulomb, st.v_string);
                st.prob_break = computeBreakingProbability(st.v_total);

                if (!broken && st.prob_break > 0.65) {
                    broken = true;
                }
                st.is_broken = broken;
                trajectory.push_back(st);
            }
            return trajectory;
        }
    };
}

int main() {
    using namespace QcdSim;
    CornellPotentialModel model;
    auto results = model.simulate(0.1, 2.5, 25);

    std::cout << "=== МОДЕЛЮВАННЯ ПОТЕНЦІАЛУ КХД ТА РОЗРИВУ СТРУНИ (C++) ===\n";
    std::cout << std::left << std::setw(8)  << "r (fm)" << " | "
              << std::setw(11) << "V_coul(GeV)" << " | "
              << std::setw(11) << "V_str(GeV)"  << " | "
              << std::setw(11) << "V_tot(GeV)"  << " | "
              << std::setw(10) << "P_break"     << " | "
              << "Стан\n";
    std::cout << std::string(72, '-') << "\n";

    std::cout << std::fixed << std::setprecision(4);
    for (const auto& st : results) {
        std::cout << std::setw(8)  << std::setprecision(2) << st.r_fm << " | "
                  << std::setw(11) << std::setprecision(4) << st.v_coulomb << " | "
                  << std::setw(11) << st.v_string << " | "
                  << std::setw(11) << st.v_total << " | "
                  << std::setw(10) << st.prob_break << " | "
                  << (st.is_broken ? "РОЗРИВ (Jet)" : "Струна q-qbar") << "\n";
    }

    return 0;
}
