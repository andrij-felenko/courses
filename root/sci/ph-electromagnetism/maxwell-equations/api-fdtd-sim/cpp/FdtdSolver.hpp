// FDTD Solver Public C++ Interface (FdtdSolver.hpp)
#pragma once

#include <vector>
#include <memory>
#include <string_view>
#include <expected>
#include <cstddef>
#include <cstdint>

namespace fdtd {

enum class Status : std::int32_t {
    Success                   =  0,
    ErrorNullPointer          = -1,
    ErrorInvalidGridSize      = -2,
    ErrorCflViolation         = -3,
    ErrorOutOfMemory          = -4,
    ErrorInvalidMaterial      = -5,
    ErrorUnstableSimulation   = -6
};

enum class FieldComponent { Ex, Ey, Ez, Hx, Hy, Hz };

struct GridConfig {
    std::size_t Nx{400}, Ny{1}, Nz{1};
    double dx{1e-3}, dy{1e-3}, dz{1e-3};
    double courant_factor{0.99};
};

struct Material {
    double eps_r{1.0};
    double mu_r{1.0};
    double sigma_e{0.0};
    double sigma_m{0.0};
};

class SolverEngine {
public:
    explicit SolverEngine(const GridConfig& config);
    ~SolverEngine() = default;

    SolverEngine(const SolverEngine&) = delete;
    SolverEngine& operator=(const SolverEngine&) = delete;
    SolverEngine(SolverEngine&&) noexcept = default;
    SolverEngine& operator=(SolverEngine&&) noexcept = default;

    [[nodiscard]] Status set_material(std::size_t i, std::size_t j, std::size_t k, const Material& mat) noexcept;
    [[nodiscard]] Status add_gaussian_source(std::size_t pos_x, double t0, double tau) noexcept;
    [[nodiscard]] Status step() noexcept;
    [[nodiscard]] Status run(std::size_t steps) noexcept;

    [[nodiscard]] std::span<const double> get_field(FieldComponent comp) const noexcept;
    [[nodiscard]] std::size_t current_step() const noexcept { return current_step_; }

private:
    GridConfig config_;
    std::size_t current_step_{0};
    std::vector<double> Ez_;
    std::vector<double> Hy_;
};

[[nodiscard]] constexpr std::string_view to_string(Status status) noexcept {
    switch (status) {
        case Status::Success:                 return "Success";
        case Status::ErrorNullPointer:        return "Error: Null pointer";
        case Status::ErrorInvalidGridSize:    return "Error: Invalid grid size";
        case Status::ErrorCflViolation:       return "Error: CFL stability violation";
        case Status::ErrorOutOfMemory:        return "Error: Out of memory";
        case Status::ErrorInvalidMaterial:    return "Error: Invalid material properties";
        case Status::ErrorUnstableSimulation: return "Error: Numerical instability detected";
    }
    return "Unknown error";
}

} // namespace fdtd
