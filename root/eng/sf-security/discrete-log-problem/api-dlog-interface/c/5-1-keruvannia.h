/**
 * @brief Ініціалізує структуру конфігурації значеннями за замовчуванням.
 */
dlog_status_t dlog_config_init_default(dlog_config_t *config);

/**
 * @brief Створює непрозорий контекст розв'язувача.
 */
dlog_status_t dlog_context_create(const dlog_config_t *config, void **out_ctx);

/**
 * @brief Звільняє всі ресурси контексту.
 */
void dlog_context_destroy(void *ctx);
