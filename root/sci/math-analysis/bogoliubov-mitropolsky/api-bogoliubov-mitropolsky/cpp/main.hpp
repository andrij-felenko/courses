#ifndef LIBBM_AVERAGING_HPP
#define LIBBM_AVERAGING_HPP

#include <expected>
#include <span>
#include <functional>
#include <memory>
#include <string_view>
#include <concepts>

namespace bm {

enum class ErrorCode {
    NullPointer = -1,
    InvalidEps = -2,
    InvalidOrder = -3,
    AllocationFailed = -4,
    Divergence = -5,
    QuadratureFailed = -6
};

[[nodiscard]] constexpr std::string_view formatError(ErrorCode err) noexcept {
    switch (err) {
        case ErrorCode::NullPointer: return "Null pointer argument provided";
        case ErrorCode::InvalidEps: return "Small parameter eps is out of bounds (0, 0.5]";
        case ErrorCode::InvalidOrder: return "Unsupported approximation order (must be 1 or 2)";
        case ErrorCode::AllocationFailed: return "Memory allocation failed";
        case ErrorCode::Divergence: return "Asymptotic expansion diverged";
        case ErrorCode::QuadratureFailed: return "Quadrature integration failed to converge";
    }
    return "Unknown error";
}

struct Config {
    double eps{0.1};
    double omega0{1.0};
    int order{2};
    size_t quadraturePoints{32};
};

struct State {
    double t{0.0};
    double amplitude{0.0};
    double phase{0.0};
    double xFull{0.0};
    double vFull{0.0};
};

using PerturbationFn = std::function<double(double x, double v)>;

template <typename T>
concept PerturbationCallable = std::is_invocable_r_v<double, T, double, double>;

class AveragingSolver {
public:
    [[nodiscard]] static std::expected<AveragingSolver, ErrorCode>
    create(const Config& config, PerturbationFn fn) noexcept;

    AveragingSolver(AveragingSolver&&) noexcept = default;
    AveragingSolver& operator=(AveragingSolver&&) noexcept = default;

    AveragingSolver(const AveragingSolver&) = delete;
    AveragingSolver& operator=(const AveragingSolver&) = delete;

    ~AveragingSolver() = default;

    [[nodiscard]] std::expected<void, ErrorCode> setInitialState(double a0, double psi0) noexcept;
    [[nodiscard]] std::expected<void, ErrorCode> step(double dt) noexcept;
    [[nodiscard]] std::expected<State, ErrorCode> getState() const noexcept;
    [[nodiscard]] std::expected<double, ErrorCode> computeU1(double a, double theta) const noexcept;

private:
    explicit AveragingSolver(const Config& config, PerturbationFn fn);

    Config config_;
    PerturbationFn perturbation_;
    State currentState_{};
};

} // namespace bm

#endif /* LIBBM_AVERAGING_HPP */
