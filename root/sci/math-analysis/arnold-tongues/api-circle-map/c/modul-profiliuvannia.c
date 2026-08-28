typedef struct {
    double execution_time_seconds;
    double iterations_per_second;
    size_t cache_misses_est;
} circle_map_perf_metrics_t;

/**
 * @brief Вимірює час виконання та продуктивність ядра.
 */
circle_map_status_t circle_map_benchmark(
    const circle_map_config_t *cfg,
    circle_map_perf_metrics_t *out_metrics
);
