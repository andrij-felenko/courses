/* dwt_profiler.c — реалізація калібрування, арифметики тактів і статистики. */
#include "dwt_profiler.h"

#include <stdio.h> /* printf перенаправлено у власний _write() на UART */

static uint32_t s_overhead;  /* такти, які з'їдає сама пара читань CYCCNT */
static bool     s_ready;

/* ARMv6-M (Cortex-M0/M0+) не має блоку DWT: за адресою 0xE0001000 або нулі,
   або HardFault на шині. Питаємо CPUID ДО першого дотику до DWT — інакше
   «перевірка» сама впаде в обробник відмови. Поле ARCHITECTURE (біти 19:16):
   0xC — ARMv6-M, 0xF — ARMv7-M і ARMv8-M. */
static bool core_has_dwt(void) {
    return ((SCB_CPUID >> 16) & 0xFU) != 0xCU;
}

/* Калібрування: беремо МІНІМУМ серії, а не середнє. Замір може лише
   подовшати — від переривання, промаху кеша чи очікування Flash, — тож
   справжня ціна пари читань це найкоротший результат. Середнє з draft-версії
   завищувало зміщення й з'їдало корисні такти коротких ділянок. */
static uint32_t calibrate_overhead(void) {
    uint32_t best = 0xFFFFFFFFU;

    for (int i = 0; i < 32; ++i) {
        __asm__ volatile("" ::: "memory"); /* бар'єр компілятора: читання не поїде */
        const uint32_t t0 = dwt_get_cycles();
        __asm__ volatile("" ::: "memory");
        const uint32_t t1 = dwt_get_cycles();

        const uint32_t delta = t1 - t0;
        if (delta < best) {
            best = delta;
        }
    }
    return best;
}

bool dwt_profiler_init(void) {
    s_ready = false;
    s_overhead = 0;

    if (!core_has_dwt()) {
        return false;
    }

    CORE_DEBUG_DEMCR |= DEMCR_TRCENA; /* без TRCENA блок DWT знеструмлений */
    DWT_LAR = DWT_LAR_KEY;            /* на M7/M33 знімає замок запису в CTRL */
    DWT_CTRL |= DWT_CYCCNTENA;
    DWT_CYCCNT = 0;

    if ((DWT_CTRL & DWT_CYCCNTENA) == 0U) {
        return false; /* біт не втримався: лічильника тактів у цьому DWT немає */
    }

    /* Біт може стояти, а лічильник — не рухатися (урізаний DWT деяких чипів).
       Дивимось, чи змінився показ за кілька тактів роботи. */
    const uint32_t probe = dwt_get_cycles();
    for (volatile int i = 0; i < 8; ++i) {
    }
    if (dwt_get_cycles() == probe) {
        return false;
    }

    s_overhead = calibrate_overhead();
    s_ready = true;
    return true;
}

uint32_t dwt_profiler_overhead(void) {
    return s_overhead;
}

uint32_t dwt_elapsed_cycles(uint32_t start_cycles) {
    const uint32_t now = dwt_get_cycles();

    /* Беззнакове віднімання за модулем 2^32 дає правильну кількість тактів
       і тоді, коли лічильник під час заміру перейшов через 0xFFFFFFFF.
       Єдина межа — ділянка коротша за повний оберт (на 216 МГц ≈ 19.9 с). */
    const uint32_t raw = now - start_cycles;

    return (raw > s_overhead) ? (raw - s_overhead) : 0U;
}

uint64_t dwt_cycles_to_ns(uint32_t cycles, uint32_t cpu_freq_hz) {
    if (cpu_freq_hz == 0U) {
        return 0U;
    }
    /* +f/2 — округлення до найближчого, інакше короткі ділянки систематично
       занижуються (на 216 МГц один такт це лише 4.63 нс). */
    const uint64_t scaled = (uint64_t)cycles * 1000000000ULL + (uint64_t)(cpu_freq_hz / 2U);
    return scaled / (uint64_t)cpu_freq_hz;
}

void profiler_invalidate_icache(void) {
    if ((SCB_CCR & SCB_CCR_IC) == 0U) {
        return; /* M3/M4: кеша інструкцій немає, інвалідувати нічого */
    }
    __asm__ volatile("dsb 0xF" ::: "memory");
    SCB_ICIALLU = 0U;
    __asm__ volatile("dsb 0xF" ::: "memory");
    __asm__ volatile("isb 0xF" ::: "memory");
}

void profiler_stats_reset(profiler_stats_t *stats) {
    stats->min_cycles = 0xFFFFFFFFU;
    stats->max_cycles = 0U;
    stats->total_cycles = 0U;
    stats->samples = 0U;
}

void profiler_stats_update(profiler_stats_t *stats, uint32_t cycles) {
    if (stats->samples == 0U) {
        /* Перший замір задає обидві межі — так структура працює навіть тоді,
           коли її просто занулили статичною ініціалізацією, без reset(). */
        stats->min_cycles = cycles;
        stats->max_cycles = cycles;
    } else {
        if (cycles < stats->min_cycles) {
            stats->min_cycles = cycles;
        }
        if (cycles > stats->max_cycles) {
            stats->max_cycles = cycles;
        }
    }
    stats->total_cycles += cycles;
    stats->samples++;
}

uint32_t profiler_stats_average(const profiler_stats_t *stats) {
    if (stats->samples == 0U) {
        return 0U;
    }
    return (uint32_t)(stats->total_cycles / stats->samples);
}

uint32_t profiler_stats_jitter(const profiler_stats_t *stats) {
    if (stats->samples == 0U) {
        return 0U;
    }
    return stats->max_cycles - stats->min_cycles; /* розкид найгіршого й найкращого */
}

void profiler_stats_report(const char *name, const profiler_stats_t *stats,
                           uint32_t cpu_freq_hz) {
    if (stats->samples == 0U) {
        printf("%-14s замірів немає\n", name);
        return;
    }

    const uint32_t avg = profiler_stats_average(stats);

    printf("%-14s n=%lu  min=%lu т (%lu нс)  avg=%lu т (%lu нс)  max=%lu т (%lu нс)  джитер=%lu т\n",
           name,
           (unsigned long)stats->samples,
           (unsigned long)stats->min_cycles,
           (unsigned long)dwt_cycles_to_ns(stats->min_cycles, cpu_freq_hz),
           (unsigned long)avg,
           (unsigned long)dwt_cycles_to_ns(avg, cpu_freq_hz),
           (unsigned long)stats->max_cycles,
           (unsigned long)dwt_cycles_to_ns(stats->max_cycles, cpu_freq_hz),
           (unsigned long)profiler_stats_jitter(stats));
}
