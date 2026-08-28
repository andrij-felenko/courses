/**
 * @file rtos_reent_hooks.c
 * @brief Інтеграція Newlib reentrancy з FreeRTOS (C99)
 */
#include "syscall_stubs.h"
#include <sys/reent.h>
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

static SemaphoreHandle_t g_malloc_mutex = NULL;
static StaticSemaphore_t g_malloc_mutex_buf;

void syscalls_rtos_init(void) {
    if (g_malloc_mutex == NULL) {
        g_malloc_mutex = xSemaphoreCreateMutexStatic(&g_malloc_mutex_buf);
    }
}

void __malloc_lock(struct _reent *r) {
    (void)r;
    /* Захоплюємо м'ютекс лише тоді, коли планувальник вже працює */
    if (xTaskGetSchedulerState() == taskSCHEDULER_RUNNING) {
        if (g_malloc_mutex != NULL) {
            xSemaphoreTake(g_malloc_mutex, portMAX_DELAY);
        }
    }
}

void __malloc_unlock(struct _reent *r) {
    (void)r;
    if (xTaskGetSchedulerState() == taskSCHEDULER_RUNNING) {
        if (g_malloc_mutex != NULL) {
            xSemaphoreGive(g_malloc_mutex);
        }
    }
}

/**
 * @brief Хук FreeRTOS при перемиканні завдання (вмикається через traceTASK_SWITCHED_IN)
 */
void vApplicationTaskSwitchedInHook(TCB_t *pxTCB) {
    #if (configUSE_NEWLIB_REENTRANT == 1)
    /* Перемикаємо глобальний покажчик Newlib на структуру поточного завдання */
    _impure_ptr = &(pxTCB->xNewLib_reent);
    #else
    (void)pxTCB;
    #endif
}
