#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <format>

struct FourProbeParams {
    double voltage_v;
    double current_a;
    double probe_spacing_m;
    double thickness_m = 0.0;
};

struct SheetResistanceResult {
    double r_raw_ohm;
    double r_sheet_ohm_sq;
    double resistivity_ohm_m;
    double c_factor;
};

enum class MeasurementError {
    InvalidInput,
    NonConvergence
};

class FourProbeCalculator {
public:
    static std::expected<SheetResistanceResult, MeasurementError> calculate(const FourProbeParams& p) noexcept {
        if (p.current_a <= 0.0 || p.voltage_v <= 0.0 || p.probe_spacing_m <= 0.0) {
            return std::unexpected(MeasurementError::InvalidInput);
        }

        const double r_raw = p.voltage_v / p.current_a;
        constexpr double c_base = std::numbers::pi / std::numbers::ln2;
        double c_thick = 1.0;

        if (p.thickness_m > 0.0 && (p.thickness_m / p.probe_spacing_m) > 0.05) {
            const double d_s = p.thickness_m / p.probe_spacing_m;
            c_thick = (std::numbers::pi * d_s) / std::log(std::sinh(d_s) / std::sinh(d_s / 2.0));
            c_thick /= c_base;
        }

        const double r_sheet = r_raw * c_base * c_thick;
        const double resistivity = (p.thickness_m > 0.0) ? (r_sheet * p.thickness_m) : 0.0;

        return SheetResistanceResult{
            .r_raw_ohm = r_raw,
            .r_sheet_ohm_sq = r_sheet,
            .resistivity_ohm_m = resistivity,
            .c_factor = c_base * c_thick
        };
    }

    static std::expected<double, MeasurementError> solve_van_der_pauw(
        double r_a, double r_b, double tol = 1e-7, int max_iter = 100) noexcept 
    {
        if (r_a <= 0.0 || r_b <= 0.0) {
            return std::unexpected(MeasurementError::InvalidInput);
        }

        double r_s = (std::numbers::pi / std::numbers::ln2) * ((r_a + r_b) / 2.0);

        for (int i = 0; i < max_iter; ++i) {
            const double exp_a = std::exp(-std::numbers::pi * r_a / r_s);
            const double exp_b = std::exp(-std::numbers::pi * r_b / r_s);
            const double f_val = exp_a + exp_b - 1.0;
            const double df_drs = (std::numbers::pi * r_a / (r_s * r_s)) * exp_a +
                                  (std::numbers::pi * r_b / (r_s * r_s)) * exp_b;

            const double dr_s = f_val / df_drs;
            r_s -= dr_s;

            if (std::abs(dr_s) < tol) {
                return r_s;
            }
        }
        return std::unexpected(MeasurementError::NonConvergence);
    }
};

int main() {
    FourProbeParams params{.voltage_v = 0.04532, .current_a = 0.001, .probe_spacing_m = 0.001, .thickness_m = 1e-7};

    if (auto res = FourProbeCalculator::calculate(params)) {
        std::cout << std::format("C++ [4-Probe] R_s: {:.4f} Ohm/sq, resistivity: {:.6e} Ohm*m\n",
                                 res->r_sheet_ohm_sq, res->resistivity_ohm_m);
    }

    if (auto vdp = FourProbeCalculator::solve_van_der_pauw(10.2, 11.5)) {
        std::cout << std::format("C++ [VdP] R_s: {:.4f} Ohm/sq\n", *vdp);
    }
    return 0;
}
