/* dwt_profiler.h — Модуль апаратного профілювання на C */
#ifndef DWT_PROFILER_H
#define DWT_PROFILER_H

#include <stdint.h>
#include <stdbool.h>

#if defined(STM32F407xx) || defined(STM32F746xx) || defined(STM32H743xx)
  #include "stm32f4xx.h" /* CMSIS-заголовок вашого чипа */
#else
  /* Базові адреси CoreDebug та DWT за стандартом ARM Cortex-M3/M4/M7 */
  #define CORE_DEBUG_DEMCR  (*(volatile uint32_t *)0xE000EDFCU)
  #define DWT_CTRL          (*(volatile uint32_t *)0xE0001000U)
  #define DWT_CYCCNT        (*(volatile uint32_t *)0xE0001004U)
  #define DEMCR_TRCENA_BIT  (1UL << 24)
  #define DWT_CYCCNTENA_BIT (1UL << 0)
#endif

typedef struct {
    uint32_t min_cycles;
    uint32_t max_cycles;
    uint64_t total_cycles;
    uint32_t samples_count;
} profiler_stats_t;

/**
 * @brief Ініціалізація DWT лічильника та калібрування накладних витрат.
 * @return true, якщо апаратний лічильник успішно запущено.
 */
bool dwt_profiler_init(void);

/**
 * @brief Отримання поточного значення лічильника тактів.
 */
static inline uint32_t dwt_get_cycles(void) {
#if defined(DWT)
    return DWT->CYCCNT;
#else
    return DWT_CYCCNT;
#endif
}

/**
 * @brief Розрахунок витрачених тактів із вирахуванням накладних витрат.
 */
uint32_t dwt_elapsed_cycles(uint32_t start_cycles);

/**
 * @brief Перерахунок тактів у наносекунди за поточною частотою ядра CPU.
 */
uint64_t dwt_cycles_to_ns(uint32_t cycles, uint32_t cpu_freq_hz);

/**
 * @brief Оновлення структури статистики новим заміром.
 */
void profiler_stats_update(profiler_stats_t *stats, uint32_t cycles);

/**
 * @brief Скидання накопиченої статистики.
 */
void profiler_stats_reset(profiler_stats_t *stats);

#endif /* DWT_PROFILER_H */
