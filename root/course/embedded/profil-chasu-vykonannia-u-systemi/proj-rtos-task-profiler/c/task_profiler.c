/* task_profiler.c — ядро профілювальника: калібрування, вимір, джитер, звіт. */
#include "task_profiler.h"

#include "dwt.h"

#include <stddef.h>
#include <stdio.h>

/* --- критична секція на PRIMASK ------------------------------------------
 * Оновлення 64-розрядного накопичувача й читання статистики мають бути
 * неподільними: інакше звіт зловить половину старого, половину нового слова. */
static inline uint32_t irq_save(void)
{
    uint32_t primask;
    __asm__ volatile("mrs %0, primask" : "=r"(primask));
    __asm__ volatile("cpsid i" ::: "memory");
    return primask;
}

static inline void irq_restore(uint32_t primask)
{
    if ((primask & 1U) == 0U) { /* переривання були дозволені — вертаємо */
        __asm__ volatile("cpsie i" ::: "memory");
    }
}

/* --- стан модуля ---------------------------------------------------------- */
static TaskStats s_tasks[PROFILER_MAX_TASKS];
static dwt_events_t s_events;
static uint32_t s_cpu_freq_hz = 168000000U;
static uint32_t s_overhead_cyc = 0U;
static bool s_ready = false;

static void stats_clear(TaskStats *t, const char *name, uint32_t period_cyc)
{
    t->name = name;
    t->expected_period_cyc = period_cyc;
    t->min_cyc = 0xFFFFFFFFU;
    t->max_cyc = 0U;
    t->total_cyc = 0ULL;
    t->call_count = 0U;
    t->max_jitter_cyc = 0U;
    t->last_start_cyc = 0U;
    t->last_duration_cyc = 0U;
    t->exc_cyc = 0U;
    t->sleep_cyc = 0U;
    t->orphan_count = 0U;
    t->mark_exc_cyc = 0U;
    t->mark_sleep_cyc = 0U;
    t->active = false;
    t->has_prev_enter = false;
}

/* Вхід. Мітку часу передає викликач — вона знята ДО перевірок і маскування,
 * тож у вимір не потрапляє зайвий пролог. */
static void stats_enter(TaskStats *t, uint32_t now)
{
    if (t->active) {
        /* другий вхід без виходу: попередній зріз ми загубили назавжди */
        t->orphan_count++;
    }

    if (t->has_prev_enter && t->expected_period_cyc != 0U) {
        /* беззнакова різниця лишається точною і через переповнення CYCCNT */
        const uint32_t actual_period = now - t->last_start_cyc;
        const uint32_t jitter = (actual_period > t->expected_period_cyc)
                                    ? (actual_period - t->expected_period_cyc)
                                    : (t->expected_period_cyc - actual_period);
        if (jitter > t->max_jitter_cyc) {
            t->max_jitter_cyc = jitter;
        }
    }

    dwt_events_sample(&s_events);
    t->mark_exc_cyc = s_events.exc_cyc;
    t->mark_sleep_cyc = s_events.sleep_cyc;
    t->last_start_cyc = now;
    t->has_prev_enter = true;
    t->active = true;
}

static void stats_exit(TaskStats *t, uint32_t stop)
{
    uint32_t elapsed;

    if (!t->active) {
        /* вихід без входу: перше перемикання контексту після старту
         * планувальника саме таке — задачу витіснили, а входу ми не бачили */
        t->orphan_count++;
        return;
    }

    elapsed = stop - t->last_start_cyc;
    /* знімаємо власний оверхед; якщо інтервал коротший за нього — це шум */
    elapsed = (elapsed > s_overhead_cyc) ? (elapsed - s_overhead_cyc) : 0U;

    dwt_events_sample(&s_events);
    t->exc_cyc += s_events.exc_cyc - t->mark_exc_cyc;
    t->sleep_cyc += s_events.sleep_cyc - t->mark_sleep_cyc;

    t->last_duration_cyc = elapsed;
    t->total_cyc += elapsed;
    t->call_count++;
    if (elapsed < t->min_cyc) {
        t->min_cyc = elapsed;
    }
    if (elapsed > t->max_cyc) {
        t->max_cyc = elapsed;
    }
    t->active = false;
}

/* Калібрування: женемо порожню пару enter/exit тим самим шляхом, що й у бою,
 * і беремо мінімум із 32 повторів. Мінімум, а не середнє: будь-яке переривання
 * чи промах кеша тільки додає тактів, тож найменший результат і є чистий
 * оверхед інструменту. */
static void calibrate_overhead(void)
{
    TaskStats probe;
    int i;

    stats_clear(&probe, "calib", 0U);
    s_overhead_cyc = 0U; /* поки калібруємось, віднімати ще нема чого */

    for (i = 0; i < 32; ++i) {
        uint32_t primask;
        const uint32_t start = dwt_cyccnt();
        primask = irq_save();
        stats_enter(&probe, start);
        irq_restore(primask);

        const uint32_t stop = dwt_cyccnt();
        primask = irq_save();
        stats_exit(&probe, stop);
        irq_restore(primask);
    }

    s_overhead_cyc = (probe.call_count > 0U) ? probe.min_cyc : 0U;
}

bool task_profiler_init(uint32_t cpu_freq_hz)
{
    uint8_t i;

    s_ready = false;
    if (cpu_freq_hz == 0U) {
        return false;
    }
    s_cpu_freq_hz = cpu_freq_hz;

    if (!dwt_enable_cycle_counter()) {
        return false;
    }
    dwt_enable_event_counters();
    dwt_events_reset(&s_events);

    for (i = 0U; i < PROFILER_MAX_TASKS; ++i) {
        stats_clear(&s_tasks[i], "-", 0U);
    }

    calibrate_overhead();
    s_ready = true;
    return true;
}

bool task_profiler_register_task(uint8_t id, const char *name, uint32_t expected_period_us)
{
    uint32_t period_cyc;
    uint32_t primask;

    if (id >= PROFILER_MAX_TASKS || name == NULL) {
        return false;
    }

    /* множимо в 64 бітах: 1 000 000 мкс на 168 МГц дають 1.68e14 тактів */
    period_cyc = (uint32_t)(((uint64_t)expected_period_us * (uint64_t)s_cpu_freq_hz) / 1000000ULL);

    primask = irq_save();
    stats_clear(&s_tasks[id], name, period_cyc);
    irq_restore(primask);
    return true;
}

void task_profiler_enter(uint8_t id)
{
    const uint32_t now = dwt_cyccnt(); /* мітку знімаємо першою дією */
    uint32_t primask;

    if (!s_ready || id >= PROFILER_MAX_TASKS) {
        return;
    }
    primask = irq_save();
    stats_enter(&s_tasks[id], now);
    irq_restore(primask);
}

void task_profiler_exit(uint8_t id)
{
    const uint32_t stop = dwt_cyccnt();
    uint32_t primask;

    if (!s_ready || id >= PROFILER_MAX_TASKS) {
        return;
    }
    primask = irq_save();
    stats_exit(&s_tasks[id], stop);
    irq_restore(primask);
}

bool task_profiler_get_stats(uint8_t id, TaskStats *out_stats)
{
    uint32_t primask;

    if (id >= PROFILER_MAX_TASKS || out_stats == NULL) {
        return false;
    }
    primask = irq_save();
    *out_stats = s_tasks[id]; /* копія цілком, поки ніхто її не оновлює */
    irq_restore(primask);
    return true;
}

uint32_t task_profiler_cyc_to_us(uint32_t cyc)
{
    return (uint32_t)(((uint64_t)cyc * 1000000ULL) / (uint64_t)s_cpu_freq_hz);
}

uint32_t task_profiler_overhead_cyc(void)
{
    return s_overhead_cyc;
}

void task_profiler_print_report(void (*print_fn)(const char *str))
{
    char buf[128];
    uint8_t i;

    if (print_fn == NULL) {
        return;
    }
    if (!s_ready) {
        print_fn("\r\nprofiler: CYCCNT недоступний, звіту немає\r\n");
        return;
    }

    snprintf(buf, sizeof buf, "\r\n== ПРОФІЛЬ ВИКОНАННЯ ==  f=%lu Гц  оверхед=%lu такт.\r\n",
             (unsigned long)s_cpu_freq_hz, (unsigned long)s_overhead_cyc);
    print_fn(buf);
    print_fn(" id  назва           викл.      min      avg      max   джитер      ISR\r\n");
    print_fn(" --  --------------  -------  -------  -------  -------  -------  -------  (мкс)\r\n");

    for (i = 0U; i < PROFILER_MAX_TASKS; ++i) {
        TaskStats t;

        if (!task_profiler_get_stats(i, &t) || t.call_count == 0U) {
            continue;
        }

        const uint32_t avg_cyc = (uint32_t)(t.total_cyc / (uint64_t)t.call_count);
        snprintf(buf, sizeof buf, "%3u  %-14s  %7lu  %7lu  %7lu  %7lu  %7lu  %7lu\r\n",
                 (unsigned)i, t.name, (unsigned long)t.call_count,
                 (unsigned long)task_profiler_cyc_to_us(t.min_cyc),
                 (unsigned long)task_profiler_cyc_to_us(avg_cyc),
                 (unsigned long)task_profiler_cyc_to_us(t.max_cyc),
                 (unsigned long)task_profiler_cyc_to_us(t.max_jitter_cyc),
                 (unsigned long)task_profiler_cyc_to_us(t.exc_cyc));
        print_fn(buf);

        if (t.orphan_count != 0U || t.sleep_cyc != 0U) {
            snprintf(buf, sizeof buf, "      неспарених: %lu, у сні: %lu такт.\r\n",
                     (unsigned long)t.orphan_count, (unsigned long)t.sleep_cyc);
            print_fn(buf);
        }
    }
}
