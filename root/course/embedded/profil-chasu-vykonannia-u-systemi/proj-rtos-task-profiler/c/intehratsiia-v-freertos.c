/* Фрагмент FreeRTOSConfig.h */
#include "task_profiler.h"

/* Викликається щоразу, коли планувальник обирає нову задачу */
#define traceTASK_SWITCHED_IN() do {                                      \
    TaskHandle_t xTask = xTaskGetCurrentTaskHandle();                     \
    UBaseType_t uxId = uxTaskGetTaskNumber(xTask);                        \
    if (uxId < PROFILER_MAX_TASKS) {                                      \
        task_profiler_enter((uint8_t)uxId);                               \
    }                                                                     \
} while(0)

/* Викликається безпосередньо перед витісненням поточної задачі */
#define traceTASK_SWITCHED_OUT() do {                                     \
    TaskHandle_t xTask = xTaskGetCurrentTaskHandle();                     \
    UBaseType_t uxId = uxTaskGetTaskNumber(xTask);                        \
    if (uxId < PROFILER_MAX_TASKS) {                                      \
        task_profiler_exit((uint8_t)uxId);                                \
    }                                                                     \
} while(0)
