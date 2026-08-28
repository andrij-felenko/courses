typedef struct {
    double golden_ratio_w;
    double critical_k;
    double lyapunov_at_critical;
} circle_map_golden_result_t;

/**
 * @brief Аналізує критичну універсальність при золотому перетині.
 */
circle_map_status_t circle_map_analyze_golden_ratio(
    size_t steps,
    circle_map_golden_result_t *out_result
);
