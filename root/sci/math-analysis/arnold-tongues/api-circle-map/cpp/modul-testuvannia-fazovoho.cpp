#include <cstdint>

namespace physics::nonlinear::api {

struct NoiseConfig {
    double noise_sigma{0.001};
    std::uint64_t random_seed{42};
};

class NoisyCircleMapSolver {
public:
    NoisyCircleMapSolver(CircleMapConfig base_config, NoiseConfig noise_config)
        : base_config_{base_config}, noise_config_{noise_config} {}

    [[nodiscard]] std::expected<SimulationResult, ApiErrorCode> solve() const noexcept;

private:
    CircleMapConfig base_config_;
    NoiseConfig noise_config_;
};

} // namespace physics::nonlinear::api
