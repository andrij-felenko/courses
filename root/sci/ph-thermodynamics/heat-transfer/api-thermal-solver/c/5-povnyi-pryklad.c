#include <stdio.h>
#include <stdlib.h>

int main(void) {
    // 1. Задати властивості алюмінію 6061-T6
    thermal_material_t mat = {
        .conductivity = 167.0,  // k [Вт/(м·К)]
        .density = 2700.0,      // ρ [кг/м³]
        .specific_heat = 896.0, // c_p [Дж/(кг·К)]
        .emissivity = 0.85      // ε (анодований)
    };

    // 2. Задати геометрію та сітку
    thermal_solver_config_t cfg = {
        .grid_x = 50,
        .grid_y = 50,
        .dx = 0.002,            // 2 мм
        .dy = 0.002,            // 2 мм
        .dt = 0.001,            // 1 мс
        .max_time = 5.0,        // 5 секунд
        .tolerance = 1e-5,
        .is_transient = true
    };

    // 3. Задати граничні умови на 4 гранях [Північ, Південь, Схід, Захід]
    thermal_bc_t bcs[4] = {
        {.type = THERMAL_BC_DIRICHLET, .value = 100.0}, // Північ: 100 °C
        {.type = THERMAL_BC_DIRICHLET, .value = 20.0},  // Південь: 20 °C
        {.type = THERMAL_BC_ROBIN, .h_coeff = 25.0, .t_ambient = 20.0}, // Схід: конвекція
        {.type = THERMAL_BC_ROBIN, .h_coeff = 25.0, .t_ambient = 20.0}  // Захід: конвекція
    };

    // 4. Перевірити стійкість
    double max_dt = thermal_get_max_stable_dt(&mat, cfg.dx, cfg.dy);
    if (cfg.dt > max_dt) {
        printf("Крок dt = %.5f завеликий! dt_max = %.5f с\n", cfg.dt, max_dt);
        cfg.dt = max_dt * 0.9; // Зменшити крок із запасом
    }

    // 5. Виділити пам'ять під вихідну сітку
    double* grid = (double*)malloc(cfg.grid_x * cfg.grid_y * sizeof(double));
    if (!grid) return 1;

    // 6. Запустити симуляцію
    thermal_status_t status = thermal_solve_2d(&cfg, &mat, bcs, grid);
    if (status == THERMAL_SUCCESS) {
        printf("Розрахунок успішно завершено. Температура в центрі: %.2f °C\n",
               grid[(cfg.grid_y / 2) * cfg.grid_x + (cfg.grid_x / 2)]);
    } else {
        printf("Помилка розв'язувача: код %d\n", status);
    }

    free(grid);
    return 0;
}
