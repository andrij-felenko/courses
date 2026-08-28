/* Структура метрик продуктивності виконання MSM */
typedef struct {
    double total_time_ms;          /* Загальний час виконання (мілісекунди) */
    double bucket_accum_time_ms;   /* Час заповнення кошиків (фаза 1) */
    double running_sum_time_ms;    /* Час зворотного зведення Running Sums (фаза 2) */
    double horner_time_ms;         /* Час міжвіконної агрегації Горнера (фаза 3) */
    uint64_t mixed_additions_cnt;  /* Кількість виконаних змішаних додавань */
    uint64_t jacobian_doublings_cnt;/* Кількість виконаних подвоєнь точок */
    double memory_bandwidth_gb_s;  /* Досягнута швидкість читання базису (ГБ/с) */
} msm_telemetry_t;

/**
 * Виконання MSM зі збором детальних метрик продуктивності.
 */
msm_status_t msm_execute_with_telemetry(
    msm_point_jacobian_t *result,
    const msm_point_affine_t *points,
    const msm_fe256_t *scalars,
    size_t n,
    const msm_config_t *config,
    msm_telemetry_t *telemetry
);
