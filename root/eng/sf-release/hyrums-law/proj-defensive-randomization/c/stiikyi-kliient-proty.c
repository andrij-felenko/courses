/* Клієнтська логіка на C */
int compare_nodes_by_id(const void *a, const void *b) {
    const ClusterNode *na = (const ClusterNode *)a;
    const ClusterNode *nb = (const ClusterNode *)b;
    if (na->node_id < nb->node_id) return -1;
    if (na->node_id > nb->node_id) return 1;
    return 0;
}

void robust_client_process(NodeRegistry *reg) {
    ClusterNode received[MAX_NODES];
    size_t count = registry_get_active(reg, received, MAX_NODES);

    /* СТІЙКИЙ ПІДХІД: клієнт не покладається на порядок з API,
       а явно сортує отримані дані перед обробкою за стабільним ключем */
    qsort(received, count, sizeof(ClusterNode), compare_nodes_by_id);

    for (size_t i = 0; i < count; i++) {
        /* Детермінована обробка: received[0] завжди має мінімальний ID */
    }
}
