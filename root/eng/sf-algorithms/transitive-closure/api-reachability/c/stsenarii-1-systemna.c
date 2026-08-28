#include "reachability.h"
#include <stdio.h>

void check_rbac_permission(void) {
    tc_config_t cfg = {
        .vertices = 1000,
        .mode = TC_MODE_WARSHALL_BITSET,
        .auto_reflexive = true
    };

    reachability_engine_t *engine = NULL;
    if (tc_engine_create(&cfg, &engine) != TC_SUCCESS) {
        fprintf(stderr, "Failed to create reachability engine\n");
        return;
    }

    // Додаємо зв'язки ролей: User 5 -> Role 12 -> Permission 105
    tc_add_edge(engine, 5, 12);
    tc_add_edge(engine, 12, 105);

    tc_compute(engine);

    bool can_access = false;
    if (tc_is_reachable(engine, 5, 105, &can_access) == TC_SUCCESS) {
        if (can_access) {
            printf("Access GRANTED for user 5 to permission 105\n");
        }
    }

    tc_engine_destroy(engine);
}
