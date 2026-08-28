#ifndef VORTICITY_SOLVER_HPP
#define VORTICITY_SOLVER_HPP

#include <vector>
#include <span>
#include <memory>
#include <system_error>
#include <cstddef>

namespace fluid {

enum class BoundaryCondition {
    Periodic,
    SlipWall,
    NoSlip
};

enum class SolverErrc {
    Success = 0,
    InvalidParameter = 1,
    OutOfMemory = 2,
    CflViolation = 3,
    PoissonConvergenceFailure = 4
};

std::error_code make_error_code(SolverErrc e);

struct SolverConfig {
    std::size_t nx{128};
    std::size_t ny{128};
    double dx{0.01};
    double dy{0.01};
    double dt{0.001};
    double viscosity{0.0};
    BoundaryCondition bc_type{BoundaryCondition::Periodic};
};

struct CirculationStats {
    double circulation{0.0};
    double vorticity_integral{0.0};
    double stokes_error{0.0};
    double baroclinic_generation{0.0};
    double viscous_dissipation{0.0};
};

struct Point2D {
    double x{0.0};
    double y{0.0};
};

class VorticitySolver {
public:
    explicit VorticitySolver(const SolverConfig& config);
    ~VorticitySolver();

    VorticitySolver(const VorticitySolver&) = delete;
    VorticitySolver& operator=(const VorticitySolver&) = delete;

    VorticitySolver(VorticitySolver&&) noexcept;
    VorticitySolver& operator=(VorticitySolver&&) noexcept;

    void set_vorticity(std::span<const double> omega_field);
    void step();

    [[nodiscard]] double get_time() const noexcept;
    [[nodiscard]] std::span<const double> get_omega() const noexcept;
    [[nodiscard]] std::span<const double> get_velocity_u() const noexcept;
    [[nodiscard]] std::span<const double> get_velocity_v() const noexcept;

    [[nodiscard]] CirculationStats compute_circulation(std::span<const Point2D> contour) const;

private:
    class Impl;
    std::unique_ptr<Impl> pimpl_;
};

} // namespace fluid

namespace std {
    template <>
    struct is_error_code_enum<fluid::SolverErrc> : true_type {};
}

#endif // VORTICITY_SOLVER_HPP
