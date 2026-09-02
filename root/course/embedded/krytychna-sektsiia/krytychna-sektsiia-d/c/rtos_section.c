/*
 * Критична секція, дружня до реального часу: маскуємо лише ті переривання,
 * які мають право звертатися до ядра ОС (пріоритети 5..15). Обробник захисту
 * за струмом і ШІМ (0..4) виконується й усередині секції — з нульовою затримкою.
 */
#include "critical_section.h"
#include "demos.h"

#if !CORTEXM_HAS_BASEPRI
#error "Модуль вимагає BASEPRI (ARMv7-M). На Cortex-M0/M0+ виключіть його зі збірки: там критична секція можлива лише через PRIMASK."
#endif

/* BASEPRI = 0 означає «маскування вимкнено», тобто порожню критичну секцію.
 * Класична пастка: пріоритет забули зсунути в старші біти байта. */
_Static_assert(MAX_SYSCALL_PRIORITY != 0U,
               "MAX_SYSCALL_PRIORITY має бути зсунуто в старші біти байта пріоритету");

#define CMD_QUEUE_LEN 8U

static rtos_cmd_t g_cmd_queue[CMD_QUEUE_LEN];
static volatile uint32_t g_cmd_head = 0U;
static volatile uint32_t g_cmd_tail = 0U;
static volatile uint32_t g_cmd_lost = 0U;

/* Викликається з фону й з обробників рівня ОС (пріоритет 5 і нижче). */
int rtos_queue_push(uint16_t id, int16_t arg)
{
    int accepted;

    /* 1. Зчитуємо поточний поріг. */
    const uint32_t saved_basepri = __get_BASEPRI();

    /* 2. BASEPRI_MAX опустить поріг, лише якщо новий суворіший за чинний,
     *    тому вкладений виклик ніколи не послабить зовнішню секцію. */
    __set_BASEPRI_MAX(MAX_SYSCALL_PRIORITY);
    COMPILER_BARRIER();

    const uint32_t next = (g_cmd_head + 1U) % CMD_QUEUE_LEN;
    if (next == g_cmd_tail) {
        g_cmd_lost++;
        accepted = 0;
    } else {
        g_cmd_queue[g_cmd_head].id = id;
        g_cmd_queue[g_cmd_head].arg = arg;
        g_cmd_head = next;
        accepted = 1;
    }

    COMPILER_BARRIER();
    /* 3. Повертаємо попередній поріг, а не нуль. */
    __set_BASEPRI(saved_basepri);

    return accepted;
}

int rtos_queue_pop(rtos_cmd_t *out)
{
    int taken;

    if (out == NULL) {
        return 0;
    }

    const uint32_t saved_basepri = __get_BASEPRI();
    __set_BASEPRI_MAX(MAX_SYSCALL_PRIORITY);
    COMPILER_BARRIER();

    if (g_cmd_head == g_cmd_tail) {
        taken = 0;
    } else {
        *out = g_cmd_queue[g_cmd_tail];
        g_cmd_tail = (g_cmd_tail + 1U) % CMD_QUEUE_LEN;
        taken = 1;
    }

    COMPILER_BARRIER();
    __set_BASEPRI(saved_basepri);

    return taken;
}
