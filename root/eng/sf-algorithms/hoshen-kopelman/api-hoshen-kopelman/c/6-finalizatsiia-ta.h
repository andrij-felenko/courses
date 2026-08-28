/* Завершення першого проходу та формування канонічних кластерів */
hk_error_t hk_finalize(hk_context_t* ctx);

/* Отримання зведеної статистики перколації */
hk_error_t hk_get_stats(const hk_context_t* ctx, hk_stats_t* stats_out);

/* Отримання масиву розмірів кластерів за канонічними індексами 1..total_clusters */
hk_error_t hk_get_cluster_sizes(
    const hk_context_t* ctx,
    int* sizes_out,
    int max_count,
    int* actual_count_out
);

/* Заміна тимчасових міток на канонічні номери 1..K у вихідному масиві */
hk_error_t hk_relabel_grid(
    const hk_context_t* ctx,
    int* grid_inout,
    size_t total_elements
);
