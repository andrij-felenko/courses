#include <iostream>
#include <memory>
#include <vector>
#include <stdexcept>
#include "hydro_stability.h"

namespace hydro {

class StabilitySolver {
private:
    hydro_grid_config_t config_;
    void* profile_{nullptr};

public:
    StabilitySolver(int N, double Re, double alpha, hydro_bc_type_t bc = HYDRO_BC_RIGID_WALL) {
        config_.N = N;
        config_.Re = Re;
        config_.alpha = alpha;
        config_.beta = 0.0;
        config_.bc_type = bc;
        config_.solver = HYDRO_SOLVER_QZ_LAPACK;
        config_.shift_real = 0.0;
        config_.shift_imag = 0.0;

        hydro_status_t st = hydro_profile_create_poiseuille(&config_, &profile_);
        if (st != HYDRO_SUCCESS) {
            throw std::runtime_error("Failed to create fluid profile: error code " + std::to_string(st));
        }
    }

    ~StabilitySolver() {
        if (profile_) {
            hydro_profile_free(profile_);
        }
    }

    StabilitySolver(const StabilitySolver&) = delete;
    StabilitySolver& operator=(const StabilitySolver&) = delete;

    [[nodiscard]] hydro_spectrum_result_t solve() const {
        hydro_spectrum_result_t result{};
        hydro_status_t st = hydro_solve_spectrum_orr_sommerfeld(profile_, &config_, &result);
        if (st != HYDRO_SUCCESS) {
            throw std::runtime_error("Orr-Sommerfeld solver failed: error code " + std::to_string(st));
        }
        return result;
    }
};

} // namespace hydro

int main() {
    try {
        hydro::StabilitySolver solver(128, 5772.2, 1.02);
        hydro_spectrum_result_t res = solver.solve();

        std::cout << "C++ Stability Solver Execution Success!\n";
        std::cout << "Max Growth Rate c_i: " << res.eigenvalues[res.max_unstable_idx].imag << "\n";

        hydro_spectrum_result_free(&res);
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
