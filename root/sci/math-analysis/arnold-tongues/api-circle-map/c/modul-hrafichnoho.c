typedef struct {
    int device_id;
    size_t threads_per_block;
} circle_map_gpu_config_t;

/**
 * @brief Виконує сканування сітки на прискорювачі GPU.
 */
circle_map_status_t circle_map_scan_grid_gpu(
    const circle_map_config_t *base_cfg,
    const circle_map_gpu_config_t *gpu_cfg,
    double omega_min, double omega_max, size_t res_omega,
    double k_min, double k_max, size_t res_k,
    double *out_w_matrix
);
