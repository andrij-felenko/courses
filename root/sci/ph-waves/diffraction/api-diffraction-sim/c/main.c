/* C Usage Example */
#include <stdio.h>
#include <stdlib.h>
#include "diffract_api.h"

int main(void) {
    diff_source_config_t source = {
        .wavelength_m = 532.0e-9,
        .refractive_index = 1.0,
        .source_amplitude = 1.0,
        .initial_phase_rad = 0.0
    };

    diff_grid_config_t grid = {
        .aperture_size_x = 1.0e-3,
        .aperture_size_y = 1.0e-3,
        .grid_nx = 1024,
        .grid_ny = 1,
        .screen_size_x = 0.05,
        .screen_size_y = 0.05,
        .enable_zero_padding = true
    };

    diff_context_handle_t ctx = NULL;
    if (diff_create_context(&source, &grid, &ctx) != DIFF_SUCCESS) {
        fprintf(stderr, "Помилка створення контексту!\n");
        return 1;
    }

    diff_set_aperture_slit(ctx, 0.1e-3);

    double* intensity = (double*)malloc(sizeof(double) * grid.grid_nx);
    if (diff_compute_field(ctx, DIFF_REGIME_FRAUNHOFER, 1.5, intensity, NULL) == DIFF_SUCCESS) {
        printf("Центральна інтенсивність: %.4e Вт/м²\n", intensity[grid.grid_nx / 2]);
    }

    free(intensity);
    diff_destroy_context(ctx);
    return 0;
}
