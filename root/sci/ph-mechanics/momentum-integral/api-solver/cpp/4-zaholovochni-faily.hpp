#ifndef MOMENTUM_SOLVER_HPP
#define MOMENTUM_SOLVER_HPP

#include <vector>
#include <span >
#include <string_view>
#include <expected>
#include <system_error>

namespace momentum {

enum class Status {
    Success = 0,
    NullPointer = -1,
    InvalidGrid = -2,
    InvalidViscosity = -3,
    SeparationDetected = -4,
    ConvergenceFailed = -5
};

enum class SolverMode {
    ThwaitesLaminar,
    PohlhausenLaminar,
    HeadTurbulent,
    CoupledTransition
};

struct FluidProperties {
    double density{1.225};                 // кг/м³ (повітря за замовчуванням)
    double kinematic_viscosity{1.5e-5};    // м²/с
    double reynolds_critical{5.0e5};
};

struct SolverConfig {
    SolverMode mode{SolverMode::ThwaitesLaminar};
    bool stop_on_separation{true};
    double initial_theta{1.0e-6};
};

struct PointInput {
    double x{0.0};
    double U_e{0.0};
    double dUe_dx{0.0};
};

struct PointResult {
    double x{0.0};
    double U_e{0.0};
    double dUe_dx{0.0};
    double theta{0.0};
    double delta_star{0.0};
    double H{2.59};
    double C_f{0.0};
    double tau_w{0.0};
    bool is_separated{false};
    bool is_turbulent{false};
};

struct SolutionSummary {
    std::vector<PointResult> points;
    double separation_x{-1.0};
    double total_friction_drag{0.0};
};

class BoundaryLayerSolver {
public:
    explicit BoundaryLayerSolver(FluidProperties fluid, SolverConfig config = {})
        : fluid_(fluid), config_(config) {}

    [[nodiscard]] std::expected<SolutionSummary, Status> solve(
        std::span<const PointInput> grid
    ) const;

    void set_config(const SolverConfig& config) { config_ = config; }
    [[nodiscard]] const SolverConfig& config() const noexcept { return config_; }
    [[nodiscard]] const FluidProperties& fluid() const noexcept { return fluid_; }

private:
    FluidProperties fluid_;
    SolverConfig config_;
};

[[nodiscard]] std::string_view to_string(Status status) noexcept;

} // namespace momentum

#endif // MOMENTUM_SOLVER_HPP
