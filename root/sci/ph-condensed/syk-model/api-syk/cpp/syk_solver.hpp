// C++17 API специфікація заголовного файлу syk_solver.hpp
#pragma once
#include <vector>
#include <complex>
#include <memory>
#include <string>
#include <stdexcept>

namespace syk {

enum class ErrorCode {
    InvalidParam,
    OutOfMemory,
    ConvergenceFailed,
    NullPointer
};

class SolverException : public std::runtime_error {
public:
    explicit SolverException(ErrorCode code, const std::string& msg)
        : std::runtime_error(msg), m_code(code) {}

    [[nodiscard]] ErrorCode code() const noexcept { return m_code; }

private:
    ErrorCode m_code;
};

struct SYKSolverConfig {
    std::size_t N_fermions{16};
    std::size_t q_body{4};
    double beta{10.0};
    double J_coupling{1.0};
    std::size_t grid_points{1024};
    double mix_alpha{0.1};
    double tolerance{1e-8};
    std::size_t max_iters{1000};
};

class SYKSolver {
public:
    explicit SYKSolver(const SYKSolverConfig& config);
    ~SYKSolver() noexcept;

    SYKSolver(const SYKSolver&) = delete;
    SYKSolver& operator=(const SYKSolver&) = delete;

    SYKSolver(SYKSolver&&) noexcept;
    SYKSolver& operator=(SYKSolver&&) noexcept;

    std::size_t solve();

    [[nodiscard]] const std::vector<double>& g_tau() const noexcept;
    [[nodiscard]] const std::vector<std::complex<double>>& g_omega() const noexcept;
    [[nodiscard]] const std::vector<std::complex<double>>& sigma_omega() const noexcept;

    [[nodiscard]] double compute_residual_entropy() const;

private:
    struct Impl;
    std::unique_ptr<Impl> m_impl;
};

} // namespace syk
