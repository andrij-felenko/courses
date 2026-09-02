/*
 * Журнал подій, у який пише і фон, і обробники переривань. Пара (head, tail)
 * міняється лише під захистом PRIMASK, і тут шаблон розписано по кроках:
 * зберегти маску -> вимкнути -> барʼєр -> робота -> барʼєр -> відновити.
 * Далі в проєкті ці пʼять рухів запаковано в irq_lock()/irq_unlock().
 */
#include <stddef.h>
#include <stdint.h>

#include "cortexm.h"
#include "demos.h"

#define LOG_CAPACITY 64U

static volatile uint8_t g_shared_buffer[LOG_CAPACITY];
static volatile uint32_t g_head = 0U;    /* куди пише виробник */
static volatile uint32_t g_tail = 0U;    /* звідки читає споживач */
static volatile uint32_t g_dropped = 0U; /* скільки подій не влізло */

/* Повертає 1, якщо подію записано, і 0, якщо журнал переповнений. */
int event_log_push(uint8_t code)
{
    int written;

    /* 1. Зберігаємо поточний стан регістра PRIMASK. */
    const uint32_t saved_primask = __get_PRIMASK();

    /* 2. Вимикаємо масковані переривання: CPSID i. */
    __disable_irq();

    /* 3. Барʼєр: оптимізатор не має права винести запис за межу секції. */
    COMPILER_BARRIER();

    const uint32_t next = (g_head + 1U) % LOG_CAPACITY;
    if (next == g_tail) {
        g_dropped++; /* черга повна — подію втрачаємо, але знаємо про це */
        written = 0;
    } else {
        g_shared_buffer[g_head] = code;
        g_head = next;
        written = 1;
    }

    /* 4. Барʼєр перед відновленням маски. */
    COMPILER_BARRIER();

    /* 5. Повертаємо саме той стан, який був до входу, а не «увімкнено». */
    __set_PRIMASK(saved_primask);

    return written;
}

int event_log_pop(uint8_t *code)
{
    int taken;

    if (code == NULL) {
        return 0;
    }

    const uint32_t saved_primask = __get_PRIMASK();
    __disable_irq();
    COMPILER_BARRIER();

    if (g_head == g_tail) {
        taken = 0;
    } else {
        *code = g_shared_buffer[g_tail];
        g_tail = (g_tail + 1U) % LOG_CAPACITY;
        taken = 1;
    }

    COMPILER_BARRIER();
    __set_PRIMASK(saved_primask);

    return taken;
}

uint32_t event_log_dropped(void)
{
    /* Одне вирівняне 32-бітне читання неподільне саме по собі — секція зайва. */
    return g_dropped;
}
