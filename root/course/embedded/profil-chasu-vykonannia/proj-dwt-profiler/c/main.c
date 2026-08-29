/* main.c — демонстрація: ACET із прогрівом, WCET із холодним кешем,
 * тривалість обробника переривання й запасний шлях через SysTick. */
#include "dwt_profiler.h"
#include "gpio_strobe.h"
#include "systick_counter.h"

#include <stdio.h>

#define CPU_FREQ_HZ 216000000UL /* STM32F7 на повній частоті: такт ≈ 4.63 нс */
#define FRAME_LEN   64U
#define TAPS        8U

static float g_frame[FRAME_LEN];
static bool  g_use_systick; /* ядро без DWT — міряємо SysTick */

static const float k_taps[TAPS] = {
    0.02f, 0.06f, 0.12f, 0.20f, 0.20f, 0.12f, 0.06f, 0.02f
};

/* noinline обов'язковий: вбудована в цикл заміру функція розчиняється
   в ньому, і лічильник покаже час чогось іншого. */
__attribute__((noinline))
static void fir_filter(float *frame, unsigned len) {
    for (unsigned i = TAPS - 1U; i < len; ++i) {
        float acc = 0.0f;
        for (unsigned k = 0; k < TAPS; ++k) {
            acc += k_taps[k] * frame[i - k];
        }
        frame[i] = acc;
    }
}

void process_urgent_sensor_event(void) {
    fir_filter(g_frame, FRAME_LEN);
}

static uint32_t bench_start(void) {
    return g_use_systick ? systick_get_value() : dwt_get_cycles();
}

static uint32_t bench_elapsed(uint32_t start) {
    return g_use_systick ? systick_elapsed_cycles(start) : dwt_elapsed_cycles(start);
}

static void fill_frame(void) {
    for (unsigned i = 0; i < FRAME_LEN; ++i) {
        g_frame[i] = (float)(i % 16U) * 0.125f;
    }
}

/* ACET: перший прогін іде з Flash у порожній кеш і завжди довший за решту.
   Прогріваємо й відкидаємо його — інакше він сам стає «максимумом». */
static void measure_acet(profiler_stats_t *stats, unsigned runs) {
    profiler_stats_reset(stats);

    fill_frame();
    fir_filter(g_frame, FRAME_LEN); /* прогрів, у статистику не йде */

    for (unsigned i = 0; i < runs; ++i) {
        fill_frame();
        const uint32_t start = bench_start();
        fir_filter(g_frame, FRAME_LEN);
        profiler_stats_update(stats, bench_elapsed(start));
    }
}

/* WCET: перед кожним прогоном викидаємо кеш інструкцій — так виглядає
   обробник, чий код витіснили інші задачі. Саме це число закладають у бюджет. */
static void measure_wcet(profiler_stats_t *stats, unsigned runs) {
    profiler_stats_reset(stats);

    for (unsigned i = 0; i < runs; ++i) {
        fill_frame();
        profiler_invalidate_icache();
        const uint32_t start = bench_start();
        fir_filter(g_frame, FRAME_LEN);
        profiler_stats_update(stats, bench_elapsed(start));
    }
}

int main(void) {
    profiler_stats_t acet;
    profiler_stats_t wcet;

    if (dwt_profiler_init()) {
        printf("DWT: накладні витрати %lu тактів\n",
               (unsigned long)dwt_profiler_overhead());
    } else {
        /* Cortex-M0/M0+ або чип з урізаним DWT — переходимо на SysTick. */
        g_use_systick = true;
        systick_counter_init();
        printf("DWT недоступний, міряємо SysTick: накладні витрати %lu тактів\n",
               (unsigned long)systick_counter_overhead());
    }

    gpio_strobe_init();

    measure_acet(&acet, 200U);
    measure_wcet(&wcet, 50U);

    profiler_stats_report("FIR ACET", &acet, CPU_FREQ_HZ);
    profiler_stats_report("FIR WCET", &wcet, CPU_FREQ_HZ);

    for (;;) {
        /* Статистику обробника наповнює EXTI0_IRQHandler; друкуємо те,
           що назбиралося між звітами. */
        if (g_isr_stats.samples >= 100U) {
            profiler_stats_report("EXTI0 ISR", &g_isr_stats, CPU_FREQ_HZ);
            profiler_stats_reset(&g_isr_stats);
        }
    }
}
