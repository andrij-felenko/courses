#include <sys/reent.h>
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

static SemaphoreHandle_t g_malloc_mutex = NULL;
static StaticSemaphore_t g_malloc_mutex_buffer;

void init_malloc_lock(void) {
    if (g_malloc_mutex == NULL) {
        g_malloc_mutex = xSemaphoreCreateMutexStatic(&g_malloc_mutex_buffer);
    }
}

void __malloc_lock(struct _reent *r) {
    (void)r;
    /* Якщо планувальник вже запущено, захоплюємо м'ютекс */
    if (xTaskGetSchedulerState() != taskSCHEDULER_NOT_STARTED) {
        if (g_malloc_mutex != NULL) {
            xSemaphoreTake(g_malloc_mutex, portMAX_DELAY);
        }
    }
}

void __malloc_unlock(struct _reent *r) {
    (void)r;
    if (xTaskGetSchedulerState() != taskSCHEDULER_NOT_STARTED) {
        if (g_malloc_mutex != NULL) {
            xSemaphoreGive(g_malloc_mutex);
        }
    }
}
