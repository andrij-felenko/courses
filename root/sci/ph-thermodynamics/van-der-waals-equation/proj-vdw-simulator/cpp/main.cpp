#include <iostream>
#include <cmath>
#include <vector>
#include <algorithm>
#include <iomanip>
#include <stdexcept>
#include <string>

class VanDerWaalsGas {
public:
    static constexpr double R = 8.314462618;

    std::string name;
    double a;
    double b;

    VanDerWaalsGas(std::string name_, double a_, double b_)
        : name(std::move(name_)), a(a_), b(b_) {}

    struct CriticalParams {
        double V_c;
        double P_c;
        double T_c;
        double Z_c;
    };

    CriticalParams getCriticalParams() const {
        double v_c = 3.0 * b;
        double p_c = a / (27.0 * b * b);
        double t_c = (8.0 * a) / (27.0 * R * b);
        double z_c = (p_c * v_c) / (R * t_c);
        return {v_c, p_c, t_c, z_c};
    }

    double calculatePressure(double v_m, double t) const {
        if (v_m <= b) {
            throw std::invalid_argument("V_m повинен бути більшим за b");
        }
        return (R * t) / (v_m - b) - a / (v_m * v_m);
    }

    std::vector<double> solveVolume(double p, double t) const {
        double a2 = -(b + (R * t) / p);
        double a1 = a / p;
        double a0 = -(a * b) / p;

        double q = (3.0 * a1 - a2 * a2) / 9.0;
        double r = (9.0 * a2 * a1 - 27.0 * a0 - 2.0 * a2 * a2 * a2) / 54.0;
        double disc = q * q * q + r * r;

        std::vector<double> roots;
        if (disc > 0.0) {
            double s = std::cbrt(r + std::sqrt(disc));
            double t_val = std::cbrt(r - std::sqrt(disc));
            roots.push_back(s + t_val - a2 / 3.0);
        } else {
            double theta = std::acos(r / std::sqrt(-(q * q * q)));
            double sqrt_q = std::sqrt(-q);
            roots.push_back(2.0 * sqrt_q * std::cos(theta / 3.0) - a2 / 3.0);
            roots.push_back(2.0 * sqrt_q * std::cos((theta + 2.0 * M_PI) / 3.0) - a2 / 3.0);
            roots.push_back(2.0 * sqrt_q * std::cos((theta + 4.0 * M_PI) / 3.0) - a2 / 3.0);
            std::sort(roots.begin(), roots.end());
        }
        return roots;
    }

    struct PhaseEquilibrium {
        double P_sat;
        double V_liquid;
        double V_gas;
    };

    PhaseEquilibrium maxwellConstruction(double t, int num_steps = 1000) const {
        auto crit = getCriticalParams();
        if (t >= crit.T_c) {
            throw std::domain_error("T має бути менше за T_c");
        }

        double p_low = 1000.0;
        double p_high = crit.P_c * 0.999;

        for (int iter = 0; iter < 60; ++iter) {
            double p_mid = (p_low + p_high) / 2.0;
            auto roots = solveVolume(p_mid, t);

            if (roots.size() < 3) {
                p_high = p_mid;
                continue;
            }

            double v1 = roots.front();
            double v3 = roots.back();
            double dv = (v3 - v1) / num_steps;
            double integral = 0.0;

            for (int i = 0; i < num_steps; ++i) {
                double v_curr = v1 + (i + 0.5) * dv;
                double p_vdw = calculatePressure(v_curr, t);
                integral += (p_vdw - p_mid) * dv;
            }

            if (integral > 0.0) {
                p_low = p_mid;
            } else {
                p_high = p_mid;
            }
        }

        double p_sat = (p_low + p_high) / 2.0;
        auto final_roots = solveVolume(p_sat, t);
        return {p_sat, final_roots.front(), final_roots.back()};
    }
};

int main() {
    VanDerWaalsGas co2("Вуглекислий газ (CO2)", 0.3643, 4.267e-5);
    auto crit = co2.getCriticalParams();

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== КРИТИЧНІ ПАРАМЕТРИ " << co2.name << " ===\n";
    std::cout << "T_c = " << (crit.T_c - 273.15) << " °C (" << crit.T_c << " K)\n";
    std::cout << "P_c = " << (crit.P_c / 1e5) << " бар\n";
    std::cout << "V_c = " << (crit.V_c * 1e6) << " см^3/моль\n";

    double t_sub = 290.0;
    auto eq = co2.maxwellConstruction(t_sub);

    std::cout << std::setprecision(3);
    std::cout << "=== ФАЗОВА РІВНОВАГА ZA T = " << t_sub << " K ===\n";
    std::cout << "P_sat = " << (eq.P_sat / 1e5) << " бар\n";
    std::cout << "V_l   = " << (eq.V_liquid * 1e6) << " см^3/моль\n";
    std::cout << "V_g   = " << (eq.V_gas * 1e6) << " см^3/моль\n";

    return 0;
}
