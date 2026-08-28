#pragma once
#include <vector>
#include <expected>
#include <span>
#include <cstddef>

namespace feigenbaum {

enum class ErrorCode {
    InvalidParam = -1,
    MaxItersReached = -2,
    DerivativeZero = -3,
    OutOfMemory = -4,
    NumericalOverflow = -5
};

struct Config {
    double r_min = 2.8;
    double r_max = 4.0;
    std::size_t r_steps = 1000;
    std::size_t transient_iters = 1000;
    std::size_t orbit_iters = 500;
};

struct SuperstablePoint {
    double r_superstable = 0.0;
    double residual = 0.0;
    std::size_t iterations = 0;
    double lyapunov = 0.0;
};

struct Constants {
    double delta = 0.0;
    double alpha = 0.0;
    double delta_error = 0.0;
    double alpha_error = 0.0;
};

class Solver {
public:
    explicit Solver(Config config) : config_(config) {}

    [[nodiscard]] std::expected<std::vector<double>, ErrorCode> 
    compute_bifurcation_mesh() const;

    [[nodiscard]] std::expected<SuperstablePoint, ErrorCode> 
    find_superstable(int period_power, double r_guess, double tol = 1e-12) const;

    [[nodiscard]] static std::expected<Constants, ErrorCode> 
    estimate_constants(std::span<const double> r_superstable_series);

    [[nodiscard]] std::expected<double, ErrorCode> 
    compute_lyapunov(double r, std::size_t num_iters = 50000) const;

private:
    Config config_;
};

} // namespace feigenbaum
