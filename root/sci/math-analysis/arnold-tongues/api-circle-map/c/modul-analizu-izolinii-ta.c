typedef struct {
    double target_w;
    double k_start;
    double k_end;
    size_t steps_k;
} circle_map_isocline_config_t;

/**
 * @brief Розраховує вектор точок ізолінії W = const.
 */
circle_map_status_t circle_map_trace_isocline(
    const circle_map_isocline_config_t *cfg,
    double *out_omega_array,
    double *out_k_array
);
