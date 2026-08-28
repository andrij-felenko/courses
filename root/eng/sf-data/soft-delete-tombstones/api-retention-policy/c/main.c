#include <stdint.h>
#include <stdbool.h>

typedef struct {
    const char *table_name;
    const char *time_column;
    const char *primary_key;
    uint32_t retention_days;
    uint32_t batch_size;
    uint32_t throttle_sleep_ms;
} PurgePolicyConfig;

typedef struct {
    uint64_t rows_scanned;
    uint64_t rows_purged;
    uint64_t batches_executed;
    uint64_t duration_ms;
    bool completed_without_errors;
} PurgeExecutionStats;

/**
 * Виконує неблокувальне порційне очищення м'яко видалених записів.
 * @param config Декларативна конфігурація таблиці та лімітів
 * @param stats Структура для запису телеметрії виконання
 * @return 0 при успіху, код помилки у разі збою
 */
int execute_chunked_purge(const PurgePolicyConfig *config, PurgeExecutionStats *stats);
