#ifndef FLOQUET_SOLVER_HPP
#define FLOQUET_SOLVER_HPP

#include <vector>
#include <complex>
#include <functional>
#include <span>
#include <expected>
#include <cstdint>

namespace Physics::Mechanics {

enum class FloquetStatus : int32_t {
    Success             =  0,
    InvalidParam        = -1,
    IntegrationFailure  = -2,
    EigenvalueFailure   = -3,
    AllocationError     = -4
};

struct FloquetConfig {
    std::size_t dim{2};
    double period{3.14159265358979323846};
    std::size_t steps{1000};
    double tolerance{1e-5};
};

struct FloquetResult {
    std::vector<double> monodromy_matrix; // row-major n x n
    std::vector<std::complex<double>> multipliers;
    std::vector<std::complex<double>> exponents;
    double max_modulus{0.0};
    double trace{0.0};
    bool is_stable{false};
};

class FloquetSolver {
public:
    using SystemMatrixFn = std::function<void(double t, std::span<double> out_flat_matrix)>;

    explicit FloquetSolver(FloquetConfig config) noexcept
        : m_config(std::move(config)) {}

    [[nodiscard]] std::expected<FloquetResult, FloquetStatus> solve(const SystemMatrixFn& sys_fn) const;

private:
    FloquetConfig m_config;

    void rk4_step(double t, double dt, std::span<double> phi, const SystemMatrixFn& sys_fn, std::vector<double>& scratch) const noexcept;
};

} // namespace Physics::Mechanics

#endif // FLOQUET_SOLVER_HPP
