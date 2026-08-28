#include <stdio.h>
#include <stdlib.h>
#include "vortex_solver.h"

int main(void) {
    vortex_solver_config_t config = {
        .num_vortices = 2,
        .core_radius_eps = 0.01,
        .core_type = VORTEX_CORE_KRASNY,
        .integrator = VORTEX_INTEGRATOR_RK4,
        .dt = 0.005,
        .is_3d = 0
    };

    vortex_point_t points[2] = {
        {.x = -0.5, .y = 0.0, .z = 0.0, .gamma =  1.0},
        {.x =  0.5, .y = 0.0, .z = 0.0, .gamma = -1.0}
    };

    void *solver = NULL;
    vortex_status_t st = vortex_system_create(&config, points, &solver);
    if (st != VORTEX_SUCCESS) {
        fprintf(stderr, "Помилка ініціалізації розв'язувача: %d\n", st);
        return 1;
    }

    vortex_invariants_t inv0;
    vortex_system_get_invariants(solver, &inv0);
    printf("Ініціалізація вихорової пари: M0 = %.6f, Total Gamma = %.2f\n", 
           inv0.angular_momentum, inv0.total_circulation);

    for (int step = 0; step < 200; step++) {
        st = vortex_system_step(solver);
        if (st != VORTEX_SUCCESS) {
            fprintf(stderr, "Чисельний збій на кроці %d: %d\n", step, st);
            break;
        }
    }

    vortex_invariants_t inv_end;
    vortex_system_get_invariants(solver, &inv_end);
    printf("Після 200 кроків: M_end = %.6f\n", inv_end.angular_momentum);

    vortex_system_free(solver);
    return 0;
}
