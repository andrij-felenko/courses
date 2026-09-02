#ifndef CS_PROFILE_H
#define CS_PROFILE_H

/*
 * Вимірювання тривалості критичної секції лічильником тактів DWT.
 *
 * DWT є на Cortex-M3/M4/M7/M33; на M0/M0+ його немає взагалі.
 * Заголовок пристрою від виробника (тут stm32f4xx.h) тягне core_cm4.h,
 * де оголошено блоки DWT і CoreDebug та змінну SystemCoreClock.
 */

#include "stm32f4xx.h"

#include "critical_section.h"

/* На частині ядер блок DWT замкнено CoreSight-регістром LAR. */
#define DWT_LAR_ADDR        0xE0001FB0U
#define DWT_LAR_UNLOCK_KEY  0xC5ACCE55U

/*
 * Повертає false, якщо лічильника тактів у цьому кристалі немає або він
 * не побіг. Мовчки міряти нулі — гірше, ніж не міряти взагалі.
 */
static inline bool cs_profile_init(void)
{
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    *(volatile uint32_t *)DWT_LAR_ADDR = DWT_LAR_UNLOCK_KEY;

    if ((DWT->CTRL & DWT_CTRL_NOCYCCNT_Msk) != 0U) {
        return false;
    }

    DWT->CYCCNT = 0U;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    /* Перевіряємо, що лічильник справді рахує: без живлення блоку трасування
       CYCCNT стоїть на місці, і всі виміри були б нульові. */
    const uint32_t probe = DWT->CYCCNT;
    __NOP();
    __NOP();
    __NOP();
    return DWT->CYCCNT != probe;
}

/* __BKPT без під'єднаного зневаджувача — це HardFault, тому питаємо CoreDebug. */
static inline bool cs_debugger_attached(void)
{
    return (CoreDebug->DHCSR & CoreDebug_DHCSR_C_DEBUGEN_Msk) != 0U;
}

typedef struct {
    uint32_t budget_cycles;  /* 0 — бюджет не перевіряємо */
    uint32_t last_cycles;
    uint32_t max_cycles;
    uint32_t overruns;
} cs_profile_t;

static inline void cs_profile_reset(cs_profile_t *st, uint32_t budget_cycles)
{
    CRITICAL_BLOCK() {
        st->budget_cycles = budget_cycles;
        st->last_cycles   = 0U;
        st->max_cycles    = 0U;
        st->overruns      = 0U;
    }
}

static inline uint32_t cs_profile_ns(uint32_t cycles)
{
    return (uint32_t)(((uint64_t)cycles * 1000000000ULL) / SystemCoreClock);
}

/* Бюджет зручніше задавати в наносекундах латентності найшвидшого ISR. */
static inline uint32_t cs_profile_cycles_for_ns(uint32_t ns)
{
    return (uint32_t)(((uint64_t)ns * SystemCoreClock) / 1000000000ULL);
}

typedef struct {
    cs_profile_t      *stats;
    critical_section_t cs;
    uint32_t           start;
} profiled_section_t;

static inline profiled_section_t profiled_section_enter(cs_profile_t *stats)
{
    profiled_section_t ps;

    ps.stats = stats;
    /*
     * Такти знімаємо ДО входу: вартість самого входу теж належить секції.
     * Якщо між читанням CYCCNT і CPSID устигне влізти переривання, його час
     * потрапить у вимір — і це чесно, бо саме такий шлях бачить задача,
     * яка чекає на звільнення даних.
     */
    ps.start = DWT->CYCCNT;
    ps.cs    = critical_section_enter();
    return ps;
}

static inline void profiled_section_exit(profiled_section_t *ps)
{
    critical_section_exit(ps->cs);

    /* Різниця беззнакових коректна й через переповнення 32-бітного лічильника. */
    const uint32_t elapsed = DWT->CYCCNT - ps->start;
    cs_profile_t  *st      = ps->stats;

    st->last_cycles = elapsed;
    if (elapsed > st->max_cycles) {
        st->max_cycles = elapsed;
    }
    if (st->budget_cycles != 0U && elapsed > st->budget_cycles) {
        st->overruns++;
        /* Зупиняємось саме на місці зриву — стек іще цілий. */
        if (cs_debugger_attached()) {
            __BKPT(0);
        }
    }
}

#define CS_PROF_BLOCK_IMPL_(psvar, oncevar, stats_ptr)                         \
    for (profiled_section_t psvar                                              \
             __attribute__((cleanup(profiled_section_exit)))                   \
             = profiled_section_enter(stats_ptr),                              \
             *oncevar = &psvar;                                                \
         oncevar != NULL;                                                      \
         oncevar = NULL)

/* Критична секція, тривалість якої лягає в статистику й порівнюється з бюджетом. */
#define PROFILED_BLOCK(stats_ptr) \
    CS_PROF_BLOCK_IMPL_(CS_ID(prof_), CS_ID(prof_once_), (stats_ptr))

#endif /* CS_PROFILE_H */
