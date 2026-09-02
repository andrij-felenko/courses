#ifndef CORTEXM_MASK_H
#define CORTEXM_MASK_H

/*
 * Критичні секції Cortex-M поверх CMSIS Core Intrinsics.
 *
 * Правило одне на всі три маски: НЕ «вимкнув — увімкнув», а «зберіг —
 * відновив». Безумовний __enable_irq() на виході з вкладеної секції
 * відкриває переривання посеред зовнішньої — це та сама гонка, від якої
 * секцію й ставили.
 */

#include "stm32f4xx.h"   /* CMSIS: __get_PRIMASK, __set_BASEPRI_MAX, __DSB... */

#include <stdbool.h>
#include <stdint.h>

/*
 * Явний бар'єр оптимізатора. Сучасні CMSIS уже мають клоббер пам'яті всередині
 * __disable_irq(), але в межах секції ми дублюємо його самі: інакше
 * оптимізатор має право винести звернення до спільних даних за межі секції.
 */
#define CORTEXM_COMPILER_BARRIER() __ASM volatile ("" ::: "memory")

typedef uint32_t cortexm_state_t;

/* ---- PRIMASK: глобальна секція (є на всіх профілях Cortex-M) ----------- */

static inline cortexm_state_t cortexm_primask_enter(void)
{
    const cortexm_state_t saved = __get_PRIMASK();
    __disable_irq();
    CORTEXM_COMPILER_BARRIER();
    return saved;
}

static inline void cortexm_primask_exit(cortexm_state_t saved)
{
    CORTEXM_COMPILER_BARRIER();
    __DSB();                 /* буфер запису має спорожнитися ДО зняття маски */
    __set_PRIMASK(saved);
    __ISB();                 /* конвеєр перечитує стан — IRQ беруться негайно */
}

/* ---- BASEPRI: селективна секція (ARMv7-M, ARMv8-M Mainline) ------------ */

#if !defined(__ARM_ARCH_6M__)

/*
 * threshold — уже закодований байт (NVIC_BASEPRI(prio) з nvic_priority.h).
 * Вхід іде через BASEPRI_MAX: у вкладеній секції поріг може лише посилитися,
 * тож внутрішній виклик із м'якшим порогом нічого не розмаскує.
 */
static inline cortexm_state_t cortexm_basepri_enter(uint32_t threshold)
{
    const cortexm_state_t saved = __get_BASEPRI();
    __set_BASEPRI_MAX(threshold);
    CORTEXM_COMPILER_BARRIER();
    return saved;
}

static inline void cortexm_basepri_exit(cortexm_state_t saved)
{
    CORTEXM_COMPILER_BARRIER();
    __DSB();
    __set_BASEPRI(saved);    /* безумовний запис: BASEPRI_MAX ослабити не вміє */
    __ISB();
}

/*
 * FAULTMASK піднімає пріоритет виконання до -1 і блокує навіть HardFault.
 * Всередині такої секції будь-яка помилка шини — це Lockup State, вихід із
 * якого лише через Reset або Watchdog. Тримати рівно стільки інструкцій,
 * скільки треба на скидання аварійного стану периферії.
 */
static inline cortexm_state_t cortexm_faultmask_enter(void)
{
    const cortexm_state_t saved = __get_FAULTMASK();
    __disable_fault_irq();
    CORTEXM_COMPILER_BARRIER();
    return saved;
}

static inline void cortexm_faultmask_exit(cortexm_state_t saved)
{
    CORTEXM_COMPILER_BARRIER();
    __DSB();
    __set_FAULTMASK(saved);
    __ISB();
}

#else /* ARMv6-M: порогу немає, будь-яка секція глобальна */

static inline cortexm_state_t cortexm_basepri_enter(uint32_t threshold)
{
    (void)threshold;
    return cortexm_primask_enter();
}

static inline void cortexm_basepri_exit(cortexm_state_t saved)
{
    cortexm_primask_exit(saved);
}

#endif /* !__ARM_ARCH_6M__ */

/* ---- IPSR: у якому контексті ми виконуємося -------------------------- */

static inline bool cortexm_in_isr(void)
{
    return __get_IPSR() != 0U;
}

/* true + номер IRQ, якщо активний саме зовнішній обробник периферії. */
static inline bool cortexm_active_irq(IRQn_Type *out_irq)
{
    const uint32_t ipsr = __get_IPSR();
    if (ipsr < 16U) {
        return false;    /* 0 — Thread Mode, 1..15 — системні виключення */
    }
    *out_irq = (IRQn_Type)(ipsr - 16U);
    return true;
}

/* ---- Реалізовано в asm/mask_ops.S ------------------------------------- */

uint32_t mask_primask_save_disable(void);
void     mask_primask_restore(uint32_t primask);
uint32_t mask_active_exception(void);
#if !defined(__ARM_ARCH_6M__)
uint32_t mask_basepri_raise(uint32_t basepri);
void     mask_basepri_restore(uint32_t basepri);
uint32_t mask_faultmask_save_disable(void);
void     mask_faultmask_restore(uint32_t faultmask);
#endif

/* ---- Реалізовано в cortexm_mask.c ------------------------------------- */

/* Перевіряє на живому кремнії те, що обіцяє документація ARM. */
bool cortexm_mask_selftest(void);

/* Інкремент без секції: LDREX/STREX там, де архітектура їх має. */
uint32_t cortexm_atomic_inc(volatile uint32_t *counter);

/* Цілісне читання 64 бітів під порогом threshold. */
uint64_t cortexm_read_u64(const volatile uint64_t *src, uint32_t threshold);

#endif /* CORTEXM_MASK_H */
