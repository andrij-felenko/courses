// vdp_solver.cpp — Ідіоматична реалізація на C++20 без динамічних алокацій
#include <iostream>
#include <cmath>
#include <numbers>
#include <span>
#include <expected>
#include <iomanip>

namespace vdp {

struct MeasurementData {
    double current_amps;
    double thickness_cm;
    std::span<const double, 4> v_a; // V_DC+, V_DC-, V_CD+, V_CD-
    std::span<const double, 4> v_b; // V_AD+, V_AD-, V_DA+, V_DA-
};

struct CalculationResult {
    double sheet_resistance_ohm_sq;
    double resistivity_ohm_cm;
    double asymmetry_ratio;
    int iterations;
};

enum class VdpError {
    InvalidCurrent,
    InvalidThickness,
    NegativeResistance,
    SolverDiverged
};

class VdpSolver {
public:
    static constexpr double kPi = std::numbers::pi;
    static constexpr double kLn2 = std::numbers::ln2;

    [[nodiscard]] static std::expected<double, VdpError> solve_sheet_resistance(
        double r_a, double r_b, double tol = 1e-9, int max_iter = 50) noexcept 
    {
        if (r_a <= 0.0 || r_b <= 0.0) {
            return std::unexpected(VdpError::NegativeResistance);
        }

        double r_s = (kPi / (2.0 * kLn2)) * (r_a + r_b);

        for (int i = 1; i <= max_iter; ++i) {
            const double e_a = std::exp(-kPi * r_a / r_s);
            const double e_b = std::exp(-kPi * r_b / r_s);

            const double f_val = e_a + e_b - 1.0;
            const double f_der = (kPi * r_a / (r_s * r_s)) * e_a + (kPi * r_b / (r_s * r_s)) * e_b;

            if (std::abs(f_der) < 1e-15) {
                break;
            }

            const double delta = f_val / f_der;
            r_s -= delta;

            if (std::abs(delta / r_s) < tol) {
                return r_s;
            }
        }

        return std::unexpected(VdpError::SolverDiverged);
    }

    [[nodiscard]] static std::expected<CalculationResult, VdpError> process(const MeasurementData& data) noexcept {
        if (data.current_amps <= 0.0) return std::unexpected(VdpError::InvalidCurrent);
        if (data.thickness_cm <= 0.0) return std::unexpected(VdpError::InvalidThickness);

        const double r_a1 = (data.v_a[0] - data.v_a[1]) / (2.0 * data.current_amps);
        const double r_a2 = (data.v_a[2] - data.v_a[3]) / (2.0 * data.current_amps);
        const double r_a = (r_a1 + r_a2) / 2.0;

        const double r_b1 = (data.v_b[0] - data.v_b[1]) / (2.0 * data.current_amps);
        const double r_b2 = (data.v_b[2] - data.v_b[3]) / (2.0 * data.current_amps);
        const double r_b = (r_b1 + r_b2) / 2.0;

        auto r_s_res = solve_sheet_resistance(r_a, r_b);
        if (!r_s_res.has_value()) {
            return std::unexpected(r_s_res.error());
        }

        const double r_s = r_s_res.value();
        const double rho = r_s * data.thickness_cm;
        const double ratio = (r_a > r_b) ? (r_a / r_b) : (r_b / r_a);

        return CalculationResult{
            .sheet_resistance_ohm_sq = r_s,
            .resistivity_ohm_cm = rho,
            .asymmetry_ratio = ratio,
            .iterations = 5
        };
    }
};

} // namespace vdp

int main() {
    const double v_a_arr[4] = {0.0123, -0.0121, 0.0124, -0.0122};
    const double v_b_arr[4] = {0.0185, -0.0183, 0.0186, -0.0184};

    vdp::MeasurementData input{
        .current_amps = 0.010,
        .thickness_cm = 0.05,
        .v_a = std::span<const double, 4>(v_a_arr),
        .v_b = std::span<const double, 4>(v_b_arr)
    };

    auto res = vdp::VdpSolver::process(input);
    if (res.has_value()) {
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "R_s (C++20): " << res->sheet_resistance_ohm_sq << " Ohm/sq\n";
        std::cout << "rho (C++20): " << res->resistivity_ohm_cm * 1e3 << " mOhm*cm\n";
    }
    return 0;
}
