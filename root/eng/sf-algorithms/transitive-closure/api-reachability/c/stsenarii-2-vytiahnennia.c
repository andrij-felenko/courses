void audit_user_permissions(reachability_engine_t *engine, size_t user_id) {
    size_t *reachable_nodes = NULL;
    size_t count = 0;

    if (tc_get_reachable_set(engine, user_id, &reachable_nodes, &count) == TC_SUCCESS) {
        printf("User %zu has access to %zu permissions/roles:\n", user_id, count);
        for (size_t i = 0; i < count; ++i) {
            printf(" - Node ID: %zu\n", reachable_nodes[i]);
        }
        free(reachable_nodes); // Обов'язкове звільнення виділеної масивної пам'яті
    }
}
