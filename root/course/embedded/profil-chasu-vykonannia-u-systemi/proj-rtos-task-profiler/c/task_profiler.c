/* task_profiler.c - Реалізація на чистому C для Cortex-M */
#include "task_profiler.h"
#include <stdio.h>

/* Апаратні адреси CoreDebug та DWT */
#define CORE_DEBUG_DEMCR        (*(volatile uint32_t*)0xE000EDFCU)
#define CORE_DEBUG_DEMCR_TRCENA (1U << 24)

#define DWT_CTRL                (*(volatile uint32_t*)0xE0001000U)
#define DWT_CTRL_CYCCNTENA      (1U << 0)
#define DWT_CYCCNT              (*(volatile uint32_t*)0xE0001004U)

static TaskStats s_tasks[PROFILER_MAX_TASKS];
static uint32_t s_cpu_freq_hz = 168000000U;
static uint32_t s_overhead_cyc = 0;

static inline uint32_t read_dwt_cycles(void) {
    return DWT_CYCCNT;
}

static void calibrate_overhead(void) {
    uint32_t start, stop;
    /* Вимірюємо тривалість двох послідовних читань */
    start = read_dwt_cycles();
    stop = read_dwt_cycles();
    s_overhead_cyc = stop - start;
}

void task_profiler_init(uint32_t cpu_freq_hz) {
    s_cpu_freq_hz = cpu_freq_hz;
    
    /* 1. Активація блоку трасування в CoreDebug */
    CORE_DEBUG_DEMCR |= CORE_DEBUG_DEMCR_TRCENA;
    
    /* 2. Скидання та активація лічильника CYCCNT у DWT */
    DWT_CYCCNT = 0U;
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;
    
    /* 3. Очищення структур статистики */
    for (int i = 0; i < PROFILER_MAX_TASKS; ++i) {
        s_tasks[i].name = "Unused";
        s_tasks[i].min_cyc = 0xFFFFFFFFU;
        s_tasks[i].max_cyc = 0U;
        s_tasks[i].total_cyc = 0ULL;
        s_tasks[i].call_count = 0U;
        s_tasks[i].max_jitter_cyc = 0U;
        s_tasks[i].last_start_cyc = 0U;
    }
    
    calibrate_overhead();
}

void task_profiler_register_task(uint8_t id, const char* name, uint32_t expected_period_us) {
    if (id >= PROFILER_MAX_TASKS) return;
    s_tasks[id].name = name;
    s_tasks[id].expected_period_cyc = (uint32_t)(((uint64_t)expected_period_us * s_cpu_freq_hz) / 1000000ULL);
    s_tasks[id].min_cyc = 0xFFFFFFFFU;
    s_tasks[id].max_cyc = 0U;
    s_tasks[id].total_cyc = 0ULL;
    s_tasks[id].call_count = 0U;
    s_tasks[id].max_jitter_cyc = 0U;
    s_tasks[id].last_start_cyc = 0U;
}

void task_profiler_enter(uint8_t id) {
    if (id >= PROFILER_MAX_TASKS) return;
    uint32_t now = read_dwt_cycles();
    TaskStats* t = &s_tasks[id];
    
    if (t->expected_period_cyc > 0 && t->last_start_cyc > 0) {
        uint32_t actual_period = now - t->last_start_cyc;
        uint32_t jitter = (actual_period > t->expected_period_cyc) 
            ? (actual_period - t->expected_period_cyc) 
            : (t->expected_period_cyc - actual_period);
        if (jitter > t->max_jitter_cyc) {
            t->max_jitter_cyc = jitter;
        }
    }
    t->last_start_cyc = now;
}

void task_profiler_exit(uint8_t id) {
    uint32_t stop = read_dwt_cycles();
    if (id >= PROFILER_MAX_TASKS) return;
    TaskStats* t = &s_tasks[id];
    
    uint32_t elapsed = stop - t->last_start_cyc;
    if (elapsed >= s_overhead_cyc) {
        elapsed -= s_overhead_cyc;
    }
    
    t->last_duration_cyc = elapsed;
    t->total_cyc += elapsed;
    t->call_count++;
    
    if (elapsed < t->min_cyc) t->min_cyc = elapsed;
    if (elapsed > t->max_cyc) t->max_cyc = elapsed;
}

void task_profiler_get_stats(uint8_t id, TaskStats* out_stats) {
    if (id < PROFILER_MAX_TASKS && out_stats != NULL) {
        *out_stats = s_tasks[id];
    }
}

void task_profiler_print_report(void (*print_fn)(const char* str)) {
    char buf[128];
    print_fn("\r\n+---------------- REAL-TIME EXECUTION PROFILE ----------------+\r\n");
    print_fn("ID  Name            Calls    Min(us)  Avg(us)  Max(us)  Jitter(us)\r\n");
    print_fn("--------------------------------------------------------------\r\n");
    
    for (uint8_t i = 0; i < PROFILER_MAX_TASKS; ++i) {
        TaskStats* t = &s_tasks[i];
        if (t->call_count == 0) continue;
        
        uint32_t min_us = (uint32_t)(((uint64_t)t->min_cyc * 1000000ULL) / s_cpu_freq_hz);
        uint32_t max_us = (uint32_t)(((uint64_t)t->max_cyc * 1000000ULL) / s_cpu_freq_hz);
        uint32_t avg_us = (uint32_t)((t->total_cyc * 1000000ULL) / ((uint64_t)t->call_count * s_cpu_freq_hz));
        uint32_t jit_us = (uint32_t)(((uint64_t)t->max_jitter_cyc * 1000000ULL) / s_cpu_freq_hz);
        
        snprintf(buf, sizeof(buf), "%-3u %-15s %-8lu %-8lu %-8lu %-8lu %-8lu\r\n",
                 i, t->name, (unsigned long)t->call_count,
                 (unsigned long)min_us, (unsigned long)avg_us,
                 (unsigned long)max_us, (unsigned long)jit_us);
        print_fn(buf);
    }
    print_fn("+------------------------------------------------------------+\r\n");
}
