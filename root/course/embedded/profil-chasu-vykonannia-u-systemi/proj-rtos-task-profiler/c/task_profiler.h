/* task_profiler.h - C API профілювальника */
#ifndef TASK_PROFILER_H
#define TASK_PROFILER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define PROFILER_MAX_TASKS 8

typedef struct {
    const char* name;
    uint32_t expected_period_cyc; /* 0 якщо спорадична */
    uint32_t min_cyc;
    uint32_t max_cyc;
    uint64_t total_cyc;
    uint32_t call_count;
    uint32_t max_jitter_cyc;
    uint32_t last_start_cyc;
    uint32_t last_duration_cyc;
} TaskStats;

void task_profiler_init(uint32_t cpu_freq_hz);
void task_profiler_register_task(uint8_t id, const char* name, uint32_t expected_period_us);
void task_profiler_enter(uint8_t id);
void task_profiler_exit(uint8_t id);
void task_profiler_get_stats(uint8_t id, TaskStats* out_stats);
void task_profiler_print_report(void (*print_fn)(const char* str));

#ifdef __cplusplus
}
#endif

#endif /* TASK_PROFILER_H */
