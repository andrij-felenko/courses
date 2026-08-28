typedef struct {
    double delta_threshold;
    size_t max_depth;
} circle_map_adaptive_config_t;

/**
 * @brief Виконує адаптивне подрібнення сітки параметрів.
 */
circle_map_status_t circle_map_scan_grid_adaptive(
    const circle_map_config_t *base_cfg,
    const circle_map_adaptive_config_t *adapt_cfg,
    double omega_min, double omega_max,
    double k_min, double k_max
);
