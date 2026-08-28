// Приклад використання C++20 API
#include <iostream>
#include <expected>
#include <span>
#include <vector>

namespace physics::electrodynamics {

class ElectrostaticEngine {
public:
    explicit ElectrostaticEngine(const GridConfig& config);
    ~ElectrostaticEngine() = default;

    ElectrostaticEngine(const ElectrostaticEngine&) = delete;
    ElectrostaticEngine& operator=(const ElectrostaticEngine&) = delete;
    ElectrostaticEngine(ElectrostaticEngine&&) noexcept = default;
    ElectrostaticEngine& operator=(ElectrostaticEngine&&) noexcept = default;

    [[nodiscard]] SimError setChargeDensity(size_t i, size_t j, size_t k, double rho);
    [[nodiscard]] SimError setRelativePermittivity(size_t i, size_t j, size_t k, double eps_r);
    [[nodiscard]] std::expected<size_t, SimError> solvePoisson(double tol = 1e-5, size_t max_iter = 1000, double omega = 1.6);
    [[nodiscard]] std::expected<GaussVerificationResult, SimError> verifyGaussLaw(size_t i1, size_t i2, size_t j1, size_t j2, size_t k1, size_t k2) const;

    [[nodiscard]] std::span<const double> getPotentialBuffer() const noexcept;
    [[nodiscard]] std::span<const double> getElectricFieldX() const noexcept;
    [[nodiscard]] std::span<const double> getElectricFieldY() const noexcept;
    [[nodiscard]] std::span<const double> getElectricFieldZ() const noexcept;

private:
    GridConfig config_;
    std::vector<double> potential_;
    std::vector<double> charge_density_;
    std::vector<double> permittivity_;
    std::vector<double> ex_;
    std::vector<double> ey_;
    std::vector<double> ez_;
};

} // namespace physics::electrodynamics
