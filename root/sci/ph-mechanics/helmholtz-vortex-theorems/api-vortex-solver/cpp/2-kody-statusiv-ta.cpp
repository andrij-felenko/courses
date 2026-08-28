#include <cstdint>
#include <string_view>

namespace vortex {

enum class Status : int32_t {
    Success             =  0,
    InvalidParam        = -1,
    OutOfMemory         = -2,
    CoreSingularity     = -3,
    IntegrationDiverged = -4,
    DimensionMismatch   = -5
};

enum class CoreType : uint8_t {
    Singular  = 0,
    Krasny    = 1,
    LambOseen = 2
};

enum class IntegratorType : uint8_t {
    Euler = 0,
    RK4   = 1
};

struct Point {
    double x{0.0};
    double y{0.0};
    double z{0.0};
    double gamma{0.0};
};

struct Config {
    int32_t num_vortices{0};
    double core_radius_eps{0.01};
    CoreType core_type{CoreType::Krasny};
    IntegratorType integrator{IntegratorType::RK4};
    double dt{0.001};
    bool is_3d{false};
};

struct Invariants {
    double total_circulation{0.0};
    double center_of_vorticity_x{0.0};
    double center_of_vorticity_y{0.0};
    double angular_momentum{0.0};
    double kinetic_energy{0.0};
};

} // namespace vortex
