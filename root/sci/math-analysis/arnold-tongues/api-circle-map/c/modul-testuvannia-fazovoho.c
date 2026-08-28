typedef struct {
    double noise_sigma;
    uint64_t random_seed;
} circle_map_noise_config_t;

/**
 * @brief Розраховує траєкторію за наявності гауссівського фазового шуму.
 */
circle_map_status_t circle_map_solve_noisy(
    const circle_map_config_t *cfg,
    const circle_map_noise_config_t *noise_cfg,
    circle_map_result_t *out_result
);
