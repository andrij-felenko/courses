#include <stdio.h>
#include <assert.h>

void run_test_suite_c(void) {
    LocalOccupancyGridC grid;
    local_grid_init(&grid, 0.0f, 0.0f);

    /* Тест 1: Запис стіни на дистанції 3.0 м */
    for (float y = -2.0f; y <= 2.0f; y += 0.1f) {
        local_grid_update_ray(&grid, 0.0f, 0.0f, 3.0f, y, true);
    }
    local_grid_inflate_obstacles(&grid, 0.4f);

    AvoidanceOutput res = local_grid_compute_vfh_tactic(&grid, 4.0f, 0.0f, 0.0f, 4.0f);
    assert(res.action == TACTIC_ACTION_BYPASS_LEFT || res.action == TACTIC_ACTION_BYPASS_RIGHT || res.action == TACTIC_ACTION_BRAKE);

    /* Тест 2: Зміщення центру карти при русі вперед на 5.0 м */
    local_grid_shift_origin(&grid, 5.0f, 0.0f);
    assert(grid.origin_world_x > 4.9f && grid.origin_world_x < 5.1f);
}
