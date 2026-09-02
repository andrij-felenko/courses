/* Хуки ядра. Із статичним розподілом пам'яті дві верхні функції обов'язкові:
   без них FreeRTOS ніде взяти пам'ять під власні задачі й проєкт не злінкується. */
#include "app.h"

static StaticTask_t s_idle_tcb;
static StackType_t  s_idle_stack[configMINIMAL_STACK_SIZE];
static StaticTask_t s_timer_tcb;
static StackType_t  s_timer_stack[configTIMER_TASK_STACK_DEPTH];

/* Сигнатура для FreeRTOS V10.x; у V11 останній параметр — configSTACK_DEPTH_TYPE *. */
void vApplicationGetIdleTaskMemory(StaticTask_t **ppxTaskBuffer,
                                   StackType_t **ppxStackBuffer,
                                   uint32_t *pulStackSize)
{
    *ppxTaskBuffer = &s_idle_tcb;
    *ppxStackBuffer = s_idle_stack;
    *pulStackSize = configMINIMAL_STACK_SIZE;
}

void vApplicationGetTimerTaskMemory(StaticTask_t **ppxTaskBuffer,
                                    StackType_t **ppxStackBuffer,
                                    uint32_t *pulStackSize)
{
    *ppxTaskBuffer = &s_timer_tcb;
    *ppxStackBuffer = s_timer_stack;
    *pulStackSize = configTIMER_TASK_STACK_DEPTH;
}

/* Вимагає configCHECK_FOR_STACK_OVERFLOW = 2 у FreeRTOSConfig.h.
   Продовжувати роботу після переповнення стека не можна: пам'ять сусідньої
   задачі вже затерта, тож єдина чесна реакція — зупинитися й дати watchdog
   перезавантажити прилад, лишивши слід у пам'яті для налагоджувача. */
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)
{
    static volatile char *volatile s_failed_task;
    static volatile TaskHandle_t s_failed_handle;

    s_failed_task = pcTaskName;
    s_failed_handle = xTask;

    taskDISABLE_INTERRUPTS();
    for (;;) { }
}

void vApplicationMallocFailedHook(void)
{
    /* Купи в цьому проєкті немає (configSUPPORT_DYNAMIC_ALLOCATION = 0),
       але хук лишається: якщо хтось увімкне динаміку — впадемо голосно. */
    taskDISABLE_INTERRUPTS();
    for (;;) { }
}
