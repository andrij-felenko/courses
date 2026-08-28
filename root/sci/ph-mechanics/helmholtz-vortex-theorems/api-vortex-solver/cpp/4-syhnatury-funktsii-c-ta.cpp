#include <vector>
#include <memory>
#include <span>
#include <expected>
#include "vortex_solver.h"

namespace vortex {

class Solver {
private:
    void* handle_{nullptr};

public:
    explicit Solver(void* handle) noexcept : handle_(handle) {}
    
    ~Solver() {
        if (handle_) {
            vortex_system_free(handle_);
        }
    }

    Solver(const Solver&) = delete;
    Solver& operator=(const Solver&) = delete;
    Solver(Solver&& rhs) noexcept : handle_(rhs.handle_) { rhs.handle_ = nullptr; }
    Solver& operator=(Solver&& rhs) noexcept {
        if (this != &rhs) {
            if (handle_) vortex_system_free(handle_);
            handle_ = rhs.handle_;
            rhs.handle_ = nullptr;
        }
        return *this;
    }

    static std::expected<Solver, Status> create(
        const Config& config, 
        std::span<const Point> init_points
    ) {
        if (init_points.size() != static_cast<size_t>(config.num_vortices)) {
            return std::unexpected(Status::InvalidParam);
        }
        void* h = nullptr;
        vortex_status_t st = vortex_system_create(
            reinterpret_cast<const vortex_solver_config_t*>(&config),
            reinterpret_cast<const vortex_point_t*>(init_points.data()),
            &h
        );
        if (st != VORTEX_SUCCESS) {
            return std::unexpected(static_cast<Status>(st));
        }
        return Solver(h);
    }

    Status step() {
        return static_cast<Status>(vortex_system_step(handle_));
    }

    [[nodiscard]] std::expected<Invariants, Status> invariants() const {
        Invariants inv{};
        vortex_status_t st = vortex_system_get_invariants(
            handle_, 
            reinterpret_cast<vortex_invariants_t*>(&inv)
        );
        if (st != VORTEX_SUCCESS) {
            return std::unexpected(static_cast<Status>(st));
        }
        return inv;
    }
};

} // namespace vortex
