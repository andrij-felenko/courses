#include <optional>
#include <expected>
#include <numbers>
#include <span>
#include <string_view>
#include <vector>

namespace physics::nonlinear::api {

enum class ApiErrorCode {
    NullPointer,
    InvalidParameter,
    ConvergenceFailure,
    OutOfMemory
};

struct CircleMapConfig {
    double omega{0.0};
    double k{0.0};
    std::size_t transient_steps{10000};
    std::size_t measure_steps{50000};
    double initial_x{0.0};
};

struct ResonanceInfo {
    int numerator{0};
    int denominator{1};
    double error{0.0};
};

struct SimulationResult {
    double rotation_number{0.0};
    std::optional<ResonanceInfo> resonance{};
    double lyapunov_exponent{0.0};
};

class CircleMapSolver {
public:
    explicit constexpr CircleMapSolver(CircleMapConfig config) noexcept
        : config_{config} {}

    [[nodiscard]] std::expected<SimulationResult, ApiErrorCode> solve(
        int max_denominator = 16,
        double tolerance = 1e-4) const noexcept;

private:
    CircleMapConfig config_;
};

} // namespace physics::nonlinear::api
