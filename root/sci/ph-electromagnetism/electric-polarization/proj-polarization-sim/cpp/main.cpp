#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <stdexcept>

namespace physics {

constexpr double EPSILON_0 = 8.8541878128e-12;

struct DielectricParams {
    double tau{8.2e-12};      // час релаксації в секундах
    double chi_stat{77.5};    // статична сприйнятливість
    double eps_inf{4.9};      // оптична діелектрична проникність
};

class DebyeRelaxationSolver {
public:
    explicit DebyeRelaxationSolver(DielectricParams params)
        : params_(params) {}

    [[nodiscard]] std::vector<double> simulate_time_response(
        std::span<const double> e_field,
        double dt
    ) const {
        if (dt <= 0.0) {
            throw std::invalid_argument("Крок по часу dt мусить бути додатним");
        }

        std::vector<double> p_out;
        p_out.reserve(e_field.size());

        double p_current = 0.0;
        for (double e_val : e_field) {
            double p_eq = EPSILON_0 * params_.chi_stat * e_val;
            double dp_dt = (p_eq - p_current) / params_.tau;
            p_current += dp_dt * dt;
            p_out.push_back(p_current);
        }

        return p_out;
    }

    [[nodiscard]] std::complex<double> compute_complex_permittivity(double freq_hz) const {
        double omega = 2.0 * std::numbers::pi * freq_hz;
        double eps_s = params_.eps_inf + params_.chi_stat;
        std::complex<double> j(0.0, 1.0);
        
        // Формула Дебая в комплексній формі: eps*(w) = eps_inf + (eps_s - eps_inf) / (1 + j*w*tau)
        return params_.eps_inf + (eps_s - params_.eps_inf) / (1.0 + j * omega * params_.tau);
    }

private:
    DielectricParams params_;
};

} // namespace physics

int main() {
    try {
        physics::DielectricParams water_params{
            .tau = 8.2e-12,
            .chi_stat = 77.5,
            .eps_inf = 4.9
        };

        physics::DebyeRelaxationSolver solver(water_params);

        std::vector<double> e_field(1000, 1.0e6); // 10^6 В/м
        double dt = 1.0e-13; // 0.1 пс

        auto p_out = solver.simulate_time_response(e_field, dt);

        std::cout << "--- Симуляція C++20 (Дебаївська релаксація) ---\n";
        std::cout << "t = 10 ps: P = " << p_out[100] << " Кл/м^2\n";
        std::cout << "t = 100 ps: P = " << p_out[999] << " Кл/м^2\n";

        // Обчислення комплексної проникності на частоті 2.45 ГГц (мікрохвильовка)
        auto eps_complex = solver.compute_complex_permittivity(2.45e9);
        std::cout << "На частоті 2.45 ГГц:\n";
        std::cout << "  eps'  (накопичення) = " << eps_complex.real() << "\n";
        std::cout << "  eps'' (втрати)      = " << -eps_complex.imag() << "\n";
    }
    catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
