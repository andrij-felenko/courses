#include <iostream>
#include <vector>
#include <memory>
#include <stdexcept>
#include "vortex_solver.h"

namespace vortex {

class System {
private:
    void* handle_{nullptr};

public:
    System(const vortex_solver_config_t& config, const std::vector<vortex_point_t>& points) {
        if (points.size() != static_cast<size_t>(config.num_vortices)) {
            throw std::invalid_argument("Vector size mismatch with config.num_vortices");
        }
        vortex_status_t st = vortex_system_create(&config, points.data(), &handle_);
        if (st != VORTEX_SUCCESS) {
            throw std::runtime_error("Failed to create vortex system: error code " + std::to_string(st));
        }
    }

    ~System() {
        if (handle_) {
            vortex_system_free(handle_);
        }
    }

    System(const System&) = delete;
    System& operator=(const System&) = delete;

    void step() {
        vortex_status_t st = vortex_system_step(handle_);
        if (st != VORTEX_SUCCESS) {
            throw std::runtime_error("Vortex solver step failed: error code " + std::to_string(st));
        }
    }

    [[nodiscard]] vortex_invariants_t invariants() const {
        vortex_invariants_t inv{};
        vortex_status_t st = vortex_system_get_invariants(handle_, &inv);
        if (st != VORTEX_SUCCESS) {
            throw std::runtime_error("Failed to query invariants: error code " + std::to_string(st));
        }
        return inv;
    }
};

} // namespace vortex

int main() {
    try {
        vortex_solver_config_t cfg{
            2, 0.01, VORTEX_CORE_KRASNY, VORTEX_INTEGRATOR_RK4, 0.005, 0
        };

        std::vector<vortex_point_t> pts = {
            {-0.5, 0.0, 0.0,  1.0},
            { 0.5, 0.0, 0.0, -1.0}
        };

        vortex::System sys(cfg, pts);
        std::cout << "C++ Vortex System initialized. M0 = " << sys.invariants().angular_momentum << "\n";

        for (int i = 0; i < 100; ++i) {
            sys.step();
        }

        std::cout << "Execution completed cleanly. Final M = " << sys.invariants().angular_momentum << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
