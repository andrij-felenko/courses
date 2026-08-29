/* dwt_profiler.h — вимірювання тривалості ділянок коду лічильником DWT->CYCCNT.
 *
 * Працює на ядрах ARMv7-M (Cortex-M3/M4/M7) та ARMv8-M (M33). На ARMv6-M
 * (Cortex-M0/M0+) блоку DWT фізично немає: dwt_profiler_init() поверне false,
 * і замір треба вести через systick_counter.h.
 *
 * Адреси регістрів однакові для всіх цих ядер (ARMv7-M ARM, глава C1),
 * тож CMSIS-заголовок конкретного чипа тут не потрібен.
 */
#ifndef DWT_PROFILER_H
#define DWT_PROFILER_H

#include <stdbool.h>
#include <stdint.h>

#define SCB_CPUID        (*(volatile uint32_t *)0xE000ED00U)
#define SCB_CCR          (*(volatile uint32_t *)0xE000ED14U)
#define SCB_ICIALLU      (*(volatile uint32_t *)0xE000EF50U)
#define CORE_DEBUG_DEMCR (*(volatile uint32_t *)0xE000EDFCU)
#define DWT_CTRL         (*(volatile uint32_t *)0xE0001000U)
#define DWT_CYCCNT       (*(volatile uint32_t *)0xE0001004U)
#define DWT_LAR          (*(volatile uint32_t *)0xE0001FB0U)

#define DEMCR_TRCENA     (1UL << 24)  /* дозвіл на тактування блоку трасування */
#define DWT_CYCCNTENA    (1UL << 0)   /* пуск лічильника тактів */
#define DWT_LAR_KEY      0xC5ACCE55UL /* M7/M33: без ключа DWT_CTRL лише для читання */
#define SCB_CCR_IC       (1UL << 17)  /* кеш інструкцій увімкнено (є лише на M7) */

/** Накопичена статистика розкиду замірів однієї ділянки. */
typedef struct {
    uint32_t min_cycles;
    uint32_t max_cycles;
    uint64_t total_cycles;
    uint32_t samples;
} profiler_stats_t;

/**
 * Вмикає лічильник тактів і калібрує накладні витрати на пару читань.
 * @return false, якщо ядро без DWT або лічильник не рушив (тоді SysTick).
 */
bool dwt_profiler_init(void);

/** Виміряні під час ініціалізації накладні витрати, у тактах. */
uint32_t dwt_profiler_overhead(void);

/** Поточний показ лічильника. Одне читання шини налагодження. */
static inline uint32_t dwt_get_cycles(void) {
    return DWT_CYCCNT;
}

/** Такти від start_cycles до цієї миті, за вирахуванням накладних витрат. */
uint32_t dwt_elapsed_cycles(uint32_t start_cycles);

/** Переведення тактів у наносекунди за поточною частотою ядра, з округленням. */
uint64_t dwt_cycles_to_ns(uint32_t cycles, uint32_t cpu_freq_hz);

/** Інвалідація кеша інструкцій — «холодний старт» для заміру WCET. */
void profiler_invalidate_icache(void);

void     profiler_stats_reset(profiler_stats_t *stats);
void     profiler_stats_update(profiler_stats_t *stats, uint32_t cycles);
uint32_t profiler_stats_average(const profiler_stats_t *stats);
uint32_t profiler_stats_jitter(const profiler_stats_t *stats);
void     profiler_stats_report(const char *name, const profiler_stats_t *stats,
                               uint32_t cpu_freq_hz);

#endif /* DWT_PROFILER_H */
