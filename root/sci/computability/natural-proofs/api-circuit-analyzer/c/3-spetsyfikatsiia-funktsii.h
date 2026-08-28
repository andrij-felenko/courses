#ifdef __cplusplus
extern "C" {
#endif

/* Ініціалізація за замовчуванням конфігурації */
natural_error_t natural_config_default(natural_config_t* config, uint32_t num_vars);

/* Створення та знищення контексту аналізатора */
natural_error_t natural_context_create(const natural_config_t* config, void** ctx_out);
void natural_context_destroy(void* ctx);

/* Оновлення таблиці істинності для аналізу */
natural_error_t natural_set_truth_table(void* ctx, const uint8_t* table_bytes, size_t table_size);

/* Виконання повного аналізу натуральності */
natural_error_t natural_analyze(void* ctx, natural_result_t* result_out);

/* Отримання текстового опису коду помилки */
const char* natural_error_string(natural_error_t err);

#ifdef __cplusplus
}
#endif
