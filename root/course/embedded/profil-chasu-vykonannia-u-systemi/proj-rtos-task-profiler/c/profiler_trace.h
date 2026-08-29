/* profiler_trace.h — під'єднання профілювальника до трасувальних гачків FreeRTOS.
 *
 * Підключається ОСТАННІМ рядком FreeRTOSConfig.h:
 *
 *     #define configUSE_TRACE_FACILITY 1
 *     #include "profiler_trace.h"
 *
 * Ідентифікатор задачі беремо з поля uxTaskNumber її TCB — його виставляють
 * викликом vTaskSetTaskNumber(handle, id) одразу після xTaskCreate, тим самим
 * id, під яким задачу зареєстровано в профілювальнику. Задачі без номера
 * (idle, службова задача таймерів) мають uxTaskNumber == 0, тож нульовий слот
 * тримаємо саме для них, а прикладні задачі нумеруємо з одиниці.
 */
#ifndef PROFILER_TRACE_H
#define PROFILER_TRACE_H

#include "task_profiler.h"

/* Макроси розкриваються всередині tasks.c, де pxCurrentTCB уже видно, а от
 * task.h звідси підключити не можна — FreeRTOSConfig.h читається з середини
 * самого ядра. Тому вся робота — у цих двох static inline функціях. */
static inline void profiler_trace_switch_in(unsigned task_number)
{
    if (task_number < PROFILER_MAX_TASKS) {
        task_profiler_enter((uint8_t)task_number);
    }
}

static inline void profiler_trace_switch_out(unsigned task_number)
{
    if (task_number < PROFILER_MAX_TASKS) {
        task_profiler_exit((uint8_t)task_number);
    }
}

/* Гачок спрацьовує щоразу, коли планувальник обрав нову задачу. Вимірюваний
 * інтервал — це ЗРІЗ виконання між двома перемиканнями, а не весь прохід
 * задачі: витіснену задачу планувальник спершу «виводить», і зріз закривається
 * достроково. Для періодичних задач з пріоритетом вище за все інше зріз і є
 * повна ітерація. */
#define traceTASK_SWITCHED_IN()  profiler_trace_switch_in((unsigned)pxCurrentTCB->uxTaskNumber)
#define traceTASK_SWITCHED_OUT() profiler_trace_switch_out((unsigned)pxCurrentTCB->uxTaskNumber)

#endif /* PROFILER_TRACE_H */
