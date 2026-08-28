#ifndef MESSAGE_TRANSLATOR_API_H
#define MESSAGE_TRANSLATOR_API_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Непрозорий дескриптор екземпляра транслятора */
typedef struct TranslatorInstance TranslatorInstance;

/* Конфігурація ініціалізації транслятора */
typedef struct {
    const char *source_system_name;
    uint32_t target_schema_version;
    bool enable_strict_validation;
    size_t scratchpad_buffer_size;
} TranslatorConfig;

/* Результат операції трансляції */
typedef struct {
    bool is_success;
    uint8_t *output_buffer;
    size_t output_size;
    
    /* Заповнюється тільки якщо is_success == false */
    uint32_t error_code;
    const char *error_description;
    uint8_t *dlq_envelope_buffer;
    size_t dlq_envelope_size;
} TranslationResult;

/* Створення та ініціалізація екземпляра транслятора */
TranslatorInstance* translator_create(const TranslatorConfig *config);

/* Трансляція одного пакету повідомлення на гарячому шляху */
TranslationResult translator_process_packet(
    TranslatorInstance *instance,
    const uint8_t *input_raw_bytes,
    size_t input_size,
    const char *traceparent_header
);

/* Звільнення пам'яті результату трансляції */
void translator_free_result(TranslationResult *result);

/* Знищення екземпляра транслятора та звільнення внутрішніх буферів */
void translator_destroy(TranslatorInstance *instance);

#ifdef __cplusplus
}
#endif

#endif /* MESSAGE_TRANSLATOR_API_H */
