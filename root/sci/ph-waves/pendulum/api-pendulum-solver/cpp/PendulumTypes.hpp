// PendulumTypes.hpp - Ідіоматичні типи даних та строго типізовані перелічення у C++20
#ifndef PENDULUM_TYPES_HPP
#define PENDULUM_TYPES_HPP

#include <cstdint>
#include <cstddef>

namespace physics {

enum class SolverMode : uint8_t {
    Euler = 0,
    Verlet = 1,
    RK4 = 2,
    AdaptiveRK45 = 3
};

enum class Status : int32_t {
    Ok = 0,
    InvalidParameter = -1,
    Divergence = -2,
    AllocationFailed = -3,
    UnsupportedMode = -4
};

struct Config {
    double length{1.0};
    double mass{1.0};
    double gravity{9.80665};
    double damping{0.0};
    double inertia{0.0};
    double pivot_dist{0.0};
    double drive_amplitude{0.0};
    double drive_frequency{0.0};
};

struct State {
    double theta{0.0};
    double omega{0.0};
    double alpha{0.0};
    double time{0.0};
    uint64_t step_count{0};
};

struct Metrics {
    double kinetic_energy{0.0};
    double potential_energy{0.0};
    double total_energy{0.0};
    double initial_energy{0.0};
    double energy_drift_pct{0.0};
};

} // namespace physics

#endif // PENDULUM_TYPES_HPP
