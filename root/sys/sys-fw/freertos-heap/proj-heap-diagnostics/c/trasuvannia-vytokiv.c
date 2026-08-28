#include "esp_heap_trace.h"
#include "esp_log.h"

#define NUM_RECORDS 100
static heap_trace_record_t trace_records[NUM_RECORDS];

void detect_memory_leaks(void (*routine_to_test)(void))
{
    /* 1. Ініціалізація трасувальника */
    ESP_ERROR_CHECK(heap_trace_init_standalone(trace_records, NUM_RECORDS));

    /* 2. Запуск запису тільки блоків, які не були звільнені */
    ESP_ERROR_CHECK(heap_trace_start(HEAP_TRACE_LEAKS));

    /* 3. Виконання досліджуваного сценарію */
    routine_to_test();

    /* 4. Зупинка трасування */
    ESP_ERROR_CHECK(heap_trace_stop());

    /* 5. Друк знайдених витоків */
    ESP_LOGI("TRACE", "Результати аналізу витоків:");
    heap_trace_dump();
}
