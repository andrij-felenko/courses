#include <cstdint>
#include <cstddef>

namespace physics::nonlinear::api {

struct SimulationState {
    double current_x{0.0};
    std::int64_t total_turns{0};
    double omega{0.0};
    double k{0.0};
    std::size_t current_step{0};
};

class StateSerializer {
public:
    [[nodiscard]] static SimulationState capture(
        double x, std::int64_t turns, double omega, double k, std::size_t step) noexcept 
    {
        return SimulationState{x, turns, omega, k, step};
    }
};

} // namespace physics::nonlinear::api
