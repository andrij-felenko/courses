/**
 * @brief Створює новий екземпляр провайдера оракула на основі скінченного масиву.
 */
otm_status_t otm_oracle_create_finite(
    const uint64_t *elements,
    size_t count,
    oracle_provider_t **out_provider
);

/**
 * @brief Здійснює запит до оракула з автоматичним протоколюванням.
 */
otm_status_t otm_oracle_query(
    oracle_provider_t *provider,
    uint64_t query_val,
    otm_query_trace_t *trace,
    bool *out_answer
);

/**
 * @brief Обчислює точне значення функції використання u(x) за трасою.
 */
uint64_t otm_trace_get_use_bound(const otm_query_trace_t *trace);

/**
 * @brief Звільняє ресурси оракула.
 */
void otm_oracle_destroy(oracle_provider_t *provider);
