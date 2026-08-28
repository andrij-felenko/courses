#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <system_error>

namespace physics::magnetics {

constexpr double mu0 = 4.0 * std::numbers::pi * 1e-7;

struct CoreMaterial {
    double k1{4.5};
    double k2{3.8};
    double k3{120.0};
    double b_sat{0.42};

    [[nodiscard]] constexpr double h_field(double b) const noexcept {
        return (k1 * std::exp(k2 * b * b) + k3) * b;
    }

    [[nodiscard]] constexpr double dh_db(double b) const noexcept {
        const double b2 = b * b;
        const double exp_val = std::exp(k2 * b2);
        return k1 * exp_val * (1.0 + 2.0 * k2 * b2) + k3;
    }
};

struct CircuitParams {
    double l_core_m;
    double l_gap_m;
    double area_m2;
    int turns;
    double current_a;
};

struct SimulationResult {
    double b_field_t;
    double flux_wb;
    double reluctance_core;
    double reluctance_gap;
    double total_reluctance;
    double inductance_h;
    int iterations;
};

enum class SolverError {
    invalid_parameters,
    non_convergence
};

[[nodiscard]] std::expected<SimulationResult, SolverError> 
solve_circuit(const CircuitParams& params, const CoreMaterial& mat) noexcept {
    if (params.l_core_m <= 0.0 || params.area_m2 <= 0.0 || params.turns <= 0) {
        return std::unexpected(SolverError::invalid_parameters);
    }

    const double mmf = params.turns * params.current_a;
    double b = 0.1;
    constexpr int max_iter = 100;
    constexpr double tol = 1e-7;

    for (int iter = 0; iter < max_iter; ++iter) {
        const double h = mat.h_field(b);
        const double f_val = h * params.l_core_m + (b / mu0) * params.l_gap_m - mmf;
        const double df_val = mat.dh_db(b) * params.l_core_m + params.l_gap_m / mu0;

        const double delta = f_val / df_val;
        b -= delta;

        if (b < 1e-6) b = 1e-6;

        if (std::abs(delta) < tol) {
            const double flux = b * params.area_m2;
            const double rm_gap = params.l_gap_m / (mu0 * params.area_m2);
            const double rm_core = (mat.h_field(b) * params.l_core_m) / flux;
            const double rm_total = rm_core + rm_gap;
            const double inductance = (params.turns * params.turns) / rm_total;

            return SimulationResult{
                .b_field_t = b,
                .flux_wb = flux,
                .reluctance_core = rm_core,
                .reluctance_gap = rm_gap,
                .total_reluctance = rm_total,
                .inductance_h = inductance,
                .iterations = iter + 1
            };
        }
    }

    return std::unexpected(SolverError::non_convergence);
}

} // namespace physics::magnetics

int main() {
    using namespace physics::magnetics;

    const CoreMaterial ferrite{};
    const CircuitParams params{
        .l_core_m = 0.114,
        .l_gap_m = 0.001,
        .area_m2 = 2.11e-4,
        .turns = 30,
        .current_a = 8.0
    };

    const auto result = solve_circuit(params, ferrite);

    if (result) {
        std::cout << "B = " << result->b_field_t << " T\n"
                  << "Flux = " << result->flux_wb * 1e6 << " uWb\n"
                  << "Rm_core = " << result->reluctance_core << " A*t/Wb\n"
                  << "Rm_gap  = " << result->reluctance_gap << " A*t/Wb\n"
                  << "L = " << result->inductance_h * 1e6 << " uH\n";
    } else {
        std::cerr << "Solver error occurred.\n";
    }
}
