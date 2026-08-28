// C++ Usage Example
#include <iostream>
#include <vector>
#include "diffract_api.h"

int main() {
    diff_source_config_t source{
        .wavelength_m = 532.0e-9, // Зелений лазер 532 нм
        .refractive_index = 1.0,
        .source_amplitude = 1.0
    };

    diff_grid_config_t grid{
        .aperture_size_x = 1.0e-3,
        .aperture_size_y = 1.0e-3,
        .grid_nx = 1024,
        .grid_ny = 1,
        .screen_size_x = 0.05,
        .screen_size_y = 0.05
    };

    diff_context_handle_t ctx = nullptr;
    if (diff_create_context(&source, &grid, &ctx) != DIFF_SUCCESS) {
        std::cerr << "Помилка створення контексту!\n";
        return 1;
    }

    diff_set_aperture_slit(ctx, 0.1e-3); // Щілина 0.1 мм

    std::vector<double> intensity(grid.grid_nx);
    diff_status_t status = diff_compute_field(
        ctx,
        DIFF_REGIME_FRAUNHOFER,
        1.5, // 1.5 метра до екрана
        intensity.data(),
        nullptr
    );

    if (status == DIFF_SUCCESS) {
        std::cout << "Центральний пік інтенсивності: " << intensity[grid.grid_nx / 2] << " Вт/м²\n";
    }

    diff_destroy_context(ctx);
    return 0;
}
