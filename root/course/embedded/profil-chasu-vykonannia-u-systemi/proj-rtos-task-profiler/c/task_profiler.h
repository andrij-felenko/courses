/* task_profiler.h — C API мікросекундного профілювальника задач і функцій. */
#ifndef TASK_PROFILER_H
#define TASK_PROFILER_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Фіксований масив контрольних точок: жодного malloc у критичних секціях. */
#define PROFILER_MAX_TASKS 8

typedef struct {
    const char *name;             /* людиночитаний ідентифікатор для звіту */
    uint32_t expected_period_cyc; /* номінальний період; 0 — спорадична точка */
    uint32_t min_cyc;             /* BCET — найкращий зафіксований час */
    uint32_t max_cyc;             /* WCET — найгірший зафіксований час */
    uint64_t total_cyc;           /* сума для ACET; 64 біти, щоб не переповнити */
    uint32_t call_count;          /* кількість завершених вимірів */
    uint32_t max_jitter_cyc;      /* найбільше відхилення періоду від номіналу */
    uint32_t last_start_cyc;      /* мітка часу останнього входу */
    uint32_t last_duration_cyc;   /* тривалість останньої завершеної ітерації */
    uint32_t exc_cyc;             /* такти переривань усередині вимірів */
    uint32_t sleep_cyc;           /* такти сну всередині вимірів (див. dwt.h) */
    uint32_t orphan_count;        /* неспарені enter/exit — ознака втраченого зрізу */

    /* нижче — службові поля, читати їх у звіті немає сенсу */
    uint32_t mark_exc_cyc;
    uint32_t mark_sleep_cyc;
    bool active;
    bool has_prev_enter;
} TaskStats;

/* Вмикає DWT, чистить статистику й калібрує власний оверхед.
 * false — CYCCNT недоступний: без відладчика домен трасування може спати. */
bool task_profiler_init(uint32_t cpu_freq_hz);

/* expected_period_us == 0 — точка спорадична, джитер для неї не рахується. */
bool task_profiler_register_task(uint8_t id, const char *name, uint32_t expected_period_us);

void task_profiler_enter(uint8_t id);
void task_profiler_exit(uint8_t id);

/* Копіює статистику під маскою переривань: 64-розрядне total_cyc на
 * 32-розрядному ядрі оновлюється двома інструкціями. */
bool task_profiler_get_stats(uint8_t id, TaskStats *out_stats);

uint32_t task_profiler_cyc_to_us(uint32_t cyc);
uint32_t task_profiler_overhead_cyc(void);

void task_profiler_print_report(void (*print_fn)(const char *str));

#ifdef __cplusplus
}
#endif

#endif /* TASK_PROFILER_H */
