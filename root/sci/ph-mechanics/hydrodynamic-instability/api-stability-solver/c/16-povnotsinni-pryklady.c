#include <stdio.h>
#include <stdlib.h>
#include "hydro_stability.h"

int main(void) {
    hydro_grid_config_t config = {
        .N = 128,
        .Re = 5772.2,       /* Критичне число Рейнольдса плоскої течії Поазейля */
        .alpha = 1.02,      /* Найнебезпечніше волнове число */
        .beta = 0.0,        /* 2D збурення за теоремою Сквайрса */
        .bc_type = HYDRO_BC_RIGID_WALL,
        .solver = HYDRO_SOLVER_QZ_LAPACK,
        .shift_real = 0.0,
        .shift_imag = 0.0
    };

    void *profile = NULL;
    hydro_status_t status = hydro_profile_create_poiseuille(&config, &profile);
    if (status != HYDRO_SUCCESS) {
        fprintf(stderr, "Помилка створення профілю Поазейля: %d\n", status);
        return 1;
    }

    hydro_spectrum_result_t result;
    status = hydro_solve_spectrum_orr_sommerfeld(profile, &config, &result);
    if (status != HYDRO_SUCCESS) {
        fprintf(stderr, "Помилка розв'язання спектральної задачі: %d\n", status);
        hydro_profile_free(profile);
        return 1;
    }

    printf("Спектральний аналіз нестійкості Поазейля (N=%d, Re=%.1f, alpha=%.2f):\n", 
           config.N, config.Re, config.alpha);
    printf("Кількість знайдених мод: %d\n", result.num_modes);
    printf("Найнестійкіша мода idx: %d\n", result.max_unstable_idx);
    printf("Фазова швидкість c_r: %.6f\n", result.eigenvalues[result.max_unstable_idx].real);
    printf("Інкремент зростання c_i: %.6f\n", result.eigenvalues[result.max_unstable_idx].imag);

    if (result.eigenvalues[result.max_unstable_idx].imag > 0.0) {
        printf("ВИСНОВОК: Потік є ЛІНІЙНО НЕСТІЙКИМ (c_i > 0)\n");
    } else {
        printf("ВИСНОВОК: Потік є СТІЙКИМ (c_i <= 0)\n");
    }

    hydro_spectrum_result_free(&result);
    hydro_profile_free(profile);
    return 0;
}
