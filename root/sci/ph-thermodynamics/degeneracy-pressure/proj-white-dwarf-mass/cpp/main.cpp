#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <utility>

constexpr double G_CONST = 6.67430e-11;
constexpr double C_SPEED = 2.99792458e8;
constexpr double M_SUN   = 1.98847e30;
constexpr double M_E     = 9.1093837e-31;
constexpr double M_U     = 1.660539066e-27;
constexpr double HBAR    = 1.054571817e-34;
constexpr double PI_VAL  = 3.14159265358979323846;

constexpr double MU_E    = 2.0;
const double B_CONST     = (8.0 * PI_VAL * std::pow(M_E * C_SPEED, 3) * MU_E * M_U) / (3.0 * std::pow(2.0 * PI_VAL * HBAR, 3));
const double A_CONST     = (PI_VAL * std::pow(M_E, 4) * std::pow(C_SPEED, 5)) / (3.0 * std::pow(2.0 * PI_VAL * HBAR, 3));

struct WhiteDwarfResult {
    double mass_solar;
    double radius_km;
};

double eos_pressure(double x) {
    if (x < 1e-4) {
        return (8.0 / 15.0) * A_CONST * std::pow(x, 5);
    }
    return A_CONST * (x * (2.0 * x * x - 3.0) * std::sqrt(1.0 + x * x) + 3.0 * std::asinh(x));
}

double eos_dp_dx(double x) {
    return 8.0 * A_CONST * std::pow(x, 4) / std::sqrt(1.0 + x * x);
}

double inv_eos_x(double p_target) {
    if (p_target <= 0.0) return 0.0;
    double x = std::pow(15.0 * p_target / (8.0 * A_CONST), 0.2);
    for (int iter = 0; iter < 25; ++iter) {
        double p_val = eos_pressure(x);
        double diff = p_val - p_target;
        if (std::abs(diff) < 1e-9 * p_target) break;
        x -= diff / eos_dp_dx(x);
        if (x < 0.0) x = 1e-10;
    }
    return x;
}

double eos_density(double x) {
    return B_CONST * std::pow(x, 3);
}

WhiteDwarfResult solve_white_dwarf(double rho_center, double dr = 500.0) {
    double x_center = std::pow(rho_center / B_CONST, 1.0 / 3.0);
    double p_center = eos_pressure(x_center);

    double r = dr;
    double m = (4.0 / 3.0) * PI_VAL * std::pow(r, 3) * rho_center;
    double p = p_center - (2.0 / 3.0) * PI_VAL * G_CONST * (rho_center * rho_center) * (r * r);

    auto derivatives = [](double r_val, double m_val, double p_val) -> std::pair<double, double> {
        if (p_val <= 0.0) return {0.0, 0.0};
        double x_val = inv_eos_x(p_val);
        double rho_val = eos_density(x_val);
        double dp_dr = - (G_CONST * m_val * rho_val) / (r_val * r_val);
        double dm_dr = 4.0 * PI_VAL * (r_val * r_val) * rho_val;
        return {dm_dr, dp_dr};
    };

    while (p > 1e-7 * p_center && r < 5e7) {
        auto [dm1, dp1] = derivatives(r, m, p);
        auto [dm2, dp2] = derivatives(r + 0.5 * dr, m + 0.5 * dr * dm1, p + 0.5 * dr * dp1);
        auto [dm3, dp3] = derivatives(r + 0.5 * dr, m + 0.5 * dr * dm2, p + 0.5 * dr * dp2);
        auto [dm4, dp4] = derivatives(r + dr, m + dr * dm3, p + dr * dp3);

        m += (dr / 6.0) * (dm1 + 2.0 * dm2 + 2.0 * dm3 + dm4);
        p += (dr / 6.0) * (dp1 + 2.0 * dp2 + 2.0 * dp3 + dp4);
        r += dr;
    }

    return {m / M_SUN, r / 1000.0};
}

int main() {
    const std::vector<double> densities = {1e8, 1e9, 1e10, 1e11, 1e12, 1e13};
    std::cout << std::setw(28) << "Центральна густина (г/см³)"
              << " | " << std::setw(10) << "Маса (M_☉)"
              << " | " << std::setw(11) << "Радіус (км)" << "\n";
    std::cout << std::string(57, '-') << "\n";

    for (double rho_c : densities) {
        WhiteDwarfResult res = solve_white_dwarf(rho_c);
        std::cout << std::scientific << std::setprecision(1) << std::setw(28) << (rho_c / 1000.0)
                  << " | " << std::fixed << std::setprecision(3) << std::setw(10) << res.mass_solar
                  << " | " << std::setprecision(1) << std::setw(11) << res.radius_km << "\n";
    }
    return 0;
}
