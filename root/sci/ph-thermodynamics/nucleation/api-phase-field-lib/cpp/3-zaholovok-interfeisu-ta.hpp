#ifndef PHASE_FIELD_LIB_H
#define PHASE_FIELD_LIB_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PF_SUCCESS = 0,
    PF_ERR_INVALID_ARG = -1,
    PF_ERR_OUT_OF_MEMORY = -2,
    PF_ERR_UNSTABLE_TIMESTEP = -3,
    PF_ERR_DIVERGENCE = -4
} pf_error_t;

typedef struct pf_grid_2d pf_grid_2d_t;

typedef struct {
    size_t nx;
    size_t ny;
    double dx;
    double dt;
    double kappa;
    double mobility;
    int use_openmp;
} pf_config_t;

pf_error_t pf_grid_create(pf_grid_2d_t** grid, const pf_config_t* config);
pf_error_t pf_grid_destroy(pf_grid_2d_t* grid);
pf_error_t pf_init_uniform_with_noise(pf_grid_2d_t* grid, double c_mean, double noise_amp);
pf_error_t pf_step_explicit(pf_grid_2d_t* grid);
pf_error_t pf_compute_free_energy(const pf_grid_2d_t* grid, double* out_energy);
const double* pf_get_concentration_ptr(const pf_grid_2d_t* grid);

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
#include <vector>
#include <span>
#include <memory>
#include <stdexcept>
#include <string>

namespace phasefield {

class PhaseFieldSolver2D {
public:
    explicit PhaseFieldSolver2D(const pf_config_t& config) {
        pf_grid_2d_t* raw_grid = nullptr;
        pf_error_t err = pf_grid_create(&raw_grid, &config);
        if (err != PF_SUCCESS) {
            throw std::runtime_error("Не вдалося створити сітку фазового поля. Код: " + std::to_string(err));
        }
        grid_.reset(raw_grid);
    }

    void initialize_uniform(double c_mean = 0.0, double noise_amp = 0.1) {
        pf_error_t err = pf_init_uniform_with_noise(grid_.get(), c_mean, noise_amp);
        if (err != PF_SUCCESS) {
            throw std::runtime_error("Помилка ініціалізації поля концентрації.");
        }
    }

    void step() {
        pf_error_t err = pf_step_explicit(grid_.get());
        if (err != PF_SUCCESS) {
            throw std::runtime_error("Помилка виконання часового кроку симуляції.");
        }
    }

    [[nodiscard]] double get_free_energy() const {
        double energy = 0.0;
        pf_error_t err = pf_compute_free_energy(grid_.get(), &energy);
        if (err != PF_SUCCESS) {
            throw std::runtime_error("Помилка розрахунку вільної енергії.");
        }
        return energy;
    }

    [[nodiscard]] std::span<const double> get_concentration_span(size_t& out_nx, size_t& out_ny) const {
        const double* ptr = pf_get_concentration_ptr(grid_.get());
        return std::span<const double>(ptr, 128 * 128);
    }

private:
    struct GridDeleter {
        void operator()(pf_grid_2d_t* ptr) const noexcept {
            if (ptr) {
                pf_grid_destroy(ptr);
            }
        }
    };

    std::unique_ptr<pf_grid_2d_t, GridDeleter> grid_;
};

} // namespace phasefield
#endif // __cplusplus

#endif // PHASE_FIELD_LIB_H
