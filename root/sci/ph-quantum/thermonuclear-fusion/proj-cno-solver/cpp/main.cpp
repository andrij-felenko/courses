#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <iomanip>
#include <string_view>

namespace cno {

enum Isotope : std::size_t {
    C12 = 0,
    N13 = 1,
    C13 = 2,
    N14 = 3,
    O15 = 4,
    N15 = 5,
    Count = 6
};

constexpr std::array<std::string_view, Isotope::Count> IsotopeNames = {
    "12C", "13N", "13C", "14N", "15O", "15N"
};

struct ReactionRates {
    double lambda1; // 12C + p -> 13N
    double lambda2; // 13N -> 13C (beta+)
    double lambda3; // 13C + p -> 14N
    double lambda4; // 14N + p -> 15O (bottleneck)
    double lambda5; // 15O -> 15N (beta+)
    double lambda6; // 15N + p -> 12C + 4He
    double hydrogen_fraction; // Y_p
};

using State = std::array<double, Isotope::Count>;

class CNOSolver {
public:
    explicit CNOSolver(ReactionRates rates) : rates_(rates) {}

    State derivatives(const State& Y) const {
        State dYdt{};
        const double yp = rates_.hydrogen_fraction;

        const double r1 = rates_.lambda1 * yp * Y[C12];
        const double r2 = rates_.lambda2 * Y[N13];
        const double r3 = rates_.lambda3 * yp * Y[C13];
        const double r4 = rates_.lambda4 * yp * Y[N14];
        const double r5 = rates_.lambda5 * Y[O15];
        const double r6 = rates_.lambda6 * yp * Y[N15];

        dYdt[C12] = r6 - r1;
        dYdt[N13] = r1 - r2;
        dYdt[C13] = r2 - r3;
        dYdt[N14] = r3 - r4;
        dYdt[O15] = r4 - r5;
        dYdt[N15] = r5 - r6;

        return dYdt;
    }

    void step_rk4(State& Y, double dt) const {
        const State k1 = derivatives(Y);

        State Y_temp{};
        for (std::size_t i = 0; i < Isotope::Count; ++i) {
            Y_temp[i] = Y[i] + 0.5 * dt * k1[i];
        }
        const State k2 = derivatives(Y_temp);

        for (std::size_t i = 0; i < Isotope::Count; ++i) {
            Y_temp[i] = Y[i] + 0.5 * dt * k2[i];
        }
        const State k3 = derivatives(Y_temp);

        for (std::size_t i = 0; i < Isotope::Count; ++i) {
            Y_temp[i] = Y[i] + dt * k3[i];
        }
        const State k4 = derivatives(Y_temp);

        for (std::size_t i = 0; i < Isotope::Count; ++i) {
            Y[i] += (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
        }
    }

private:
    ReactionRates rates_;
};

} // namespace cno

int main() {
    cno::ReactionRates rates{
        .lambda1 = 1.2e-4,
        .lambda2 = 1.159e-3,
        .lambda3 = 4.5e-4,
        .lambda4 = 1.8e-6,
        .lambda5 = 5.681e-3,
        .lambda6 = 8.0e-2,
        .hydrogen_fraction = 0.70
    };

    cno::CNOSolver solver(rates);
    cno::State Y{1.0, 0.0, 0.0, 0.0, 0.0, 0.0}; // Початковий склад: чистий 12C

    double time = 0.0;
    const double dt = 100.0;
    const double t_max = 1.0e7;

    std::cout << "=== Симуляція нуклеосинтезу CNO-циклу (C++) ===\n";
    std::cout << std::setw(10) << "Час (с)";
    for (auto name : cno::IsotopeNames) {
        std::cout << std::setw(10) << name;
    }
    std::cout << "\n-------------------------------------------------------------------------\n";

    std::size_t step_count = 0;
    while (step_count * dt <= t_max) {
        if (step_count % 2000 == 0) {
            std::cout << std::scientific << std::setprecision(1) << std::setw(10) << time;
            std::cout << std::fixed << std::setprecision(4);
            for (double val : Y) {
                std::cout << std::setw(10) << val;
            }
            std::cout << '\n';
        }
        solver.step_rk4(Y, dt);
        time += dt;
        ++step_count;
    }

    std::cout << "-------------------------------------------------------------------------\n";
    std::cout << "Підсумкова частка 14N: " << std::fixed << std::setprecision(2)
              << (Y[cno::N14] * 100.0) << "%\n";

    return 0;
}
