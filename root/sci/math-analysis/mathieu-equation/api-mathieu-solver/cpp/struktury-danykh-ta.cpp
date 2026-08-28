// C++20 Типи даних та структури конфігурації
#include <array>
#include <vector>
#include <cstddef>

namespace mathieu::solver {

enum class Status : int {
    Success = 0,
    InvalidParam = -1,
    NoConvergence = -2,
    OutOfMemory = -3,
    Divergence = -4
};

enum class Method {
    RK4 = 0,
    DormandPrince = 1,
    ContinuedFractions = 2
};

enum class StabilityState {
    Stable = 0,
    Unstable = 1,
    Boundary = 2
};

struct Config {
    Method method{Method::RK4};
    int period_steps{1000};
    double abs_tolerance{1e-9};
    double rel_tolerance{1e-8};
    int max_iterations{500};
};

struct PointResult {
    double a{0.0};
    double q{0.0};
    std::array<std::array<double, 2>, 2> monodromy{};
    double trace{0.0};
    double floquet_exponent{0.0};
    double floquet_nu{0.0};
    StabilityState state{StabilityState::Stable};
};

struct Grid {
    double q_min{0.0}, q_max{1.0};
    double a_min{0.0}, a_max{1.0};
    std::size_t q_res{100}, a_res{100};
    std::vector<StabilityState> data{};
};

} // namespace mathieu::solver
