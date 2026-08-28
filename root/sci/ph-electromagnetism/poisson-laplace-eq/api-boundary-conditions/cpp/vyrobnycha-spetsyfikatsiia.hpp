#ifndef POISSON_BOUNDARY_CONDITIONS_API_HPP
#define POISSON_BOUNDARY_CONDITIONS_API_HPP

#include <vector>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <string_view>

namespace physics::api {

enum class BoundaryType : std::uint8_t {
    Dirichlet,
    Neumann,
    Robin,
    Floating,
    Periodic
};

enum class SolverAlgorithm : std::uint8_t {
    Jacobi,
    GaussSeidel,
    SOR,
    PCG_ICCG,
    Multigrid
};

enum class ErrorCode : std::uint32_t {
    Success = 0,
    InvalidGridDimensions,
    NullPointer,
    OutOfMemory,
    MaxIterationsExceeded,
    DivergenceDetected,
    UnboundedNeumannProblem
};

struct BoundaryDescriptor {
    BoundaryType type{BoundaryType::Dirichlet};
    double v_value{0.0};
    double flux_value{0.0};
    double alpha_coeff{1.0};
    double beta_coeff{0.0};
    double gamma_target{0.0};
    double q_total{0.0};
};

struct GridGeometry {
    std::uint32_t dim{2};
    std::size_t nx{100};
    std::size_t ny{100};
    std::size_t nz{1};
    double dx{1e-3};
    double dy{1e-3};
    double dz{1e-3};
    double eps_r_default{1.0};
};

struct SolverSettings {
    SolverAlgorithm algorithm{SolverAlgorithm::SOR};
    double tolerance{1e-6};
    std::size_t max_iterations{10000};
    double omega_override{0.0};
};

struct ExecutionMetrics {
    std::size_t iterations_spent{0};
    double final_residual{0.0};
    double execution_time_ms{0.0};
    double total_energy_joules{0.0};
};

/* Сучасний C++23 RAII контракт сервісу розв'язувача */
class BoundaryValueProblemSolver {
public:
    explicit BoundaryValueProblemSolver(GridGeometry geometry, SolverSettings settings);

    /* Задання граничної умови для конкретного вузла */
    void set_node_boundary(std::size_t i, std::size_t j, BoundaryDescriptor descriptor);

    /* Задання джерела об'ємного заряду */
    void set_charge_density(std::size_t i, std::size_t j, double rho_coulombs_m3);

    /* Виконання чисельного розв'язання з поверненням std::expected */
    [[nodiscard]] std::expected<ExecutionMetrics, ErrorCode> execute();

    /* Отримання готового буфера потенціалів */
    [[nodiscard]] const std::vector<double>& get_potential_map() const noexcept { return potential_map_; }

private:
    GridGeometry geometry_;
    SolverSettings settings_;
    std::vector<double> potential_map_;
    std::vector<double> charge_map_;
    std::vector<BoundaryDescriptor> boundary_map_;
};

} // namespace physics::api

#endif /* POISSON_BOUNDARY_CONDITIONS_API_HPP */
