/*
 * Мінімальний зріз інтринсиків ядра Cortex-M для GCC/Clang.
 * У бойовій прошивці ці функції дає CMSIS (core_cm4.h -> cmsis_gcc.h).
 * Тут вони виписані навмисне: видно, у яку саме інструкцію ядра
 * перетворюється кожен виклик, і приклад збирається без дерева CMSIS.
 */
#ifndef CORTEXM_H
#define CORTEXM_H

#include <stdint.h>

/* Cortex-M0/M0+ (ARMv6-M) не має ні BASEPRI, ні монітора ексклюзивності. */
#if defined(__ARM_ARCH_6M__)
#define CORTEXM_HAS_BASEPRI   0
#define CORTEXM_HAS_EXCLUSIVE 0
#else
#define CORTEXM_HAS_BASEPRI   1
#define CORTEXM_HAS_EXCLUSIVE 1
#endif

/* Скільки бітів пріоритету реалізовано в NVIC. У справжньому проєкті число
 * приходить з device-заголовка (stm32f4xx.h тощо) — тут лише запасний варіант. */
#ifndef __NVIC_PRIO_BITS
#define __NVIC_PRIO_BITS 4U
#endif

/* Барʼєр компілятора: ані читання, ані запис не переїжджають через цю межу. */
#define COMPILER_BARRIER() __asm volatile("" ::: "memory")

#ifndef __CMSIS_GCC_H /* CMSIS уже підключено — його інтринсики мають перевагу */

static inline uint32_t __get_PRIMASK(void)
{
    uint32_t primask;
    __asm volatile("MRS %0, primask" : "=r"(primask)::"memory");
    return primask;
}

static inline void __set_PRIMASK(uint32_t primask)
{
    __asm volatile("MSR primask, %0" ::"r"(primask) : "memory");
}

static inline void __disable_irq(void) { __asm volatile("CPSID i" ::: "memory"); }
static inline void __enable_irq(void) { __asm volatile("CPSIE i" ::: "memory"); }

/* Апаратний барʼєр памʼяті. Потрібен там, де на ту саму памʼять дивиться ще
 * хтось (друге ядро, DMA), а не лише оптимізатор компілятора. */
static inline void __DMB(void) { __asm volatile("DMB 0xF" ::: "memory"); }

#if CORTEXM_HAS_BASEPRI
static inline uint32_t __get_BASEPRI(void)
{
    uint32_t basepri;
    __asm volatile("MRS %0, basepri" : "=r"(basepri)::"memory");
    return basepri;
}

static inline void __set_BASEPRI(uint32_t basepri)
{
    __asm volatile("MSR basepri, %0" ::"r"(basepri) : "memory");
}

/* BASEPRI_MAX записує нове значення, ЛИШЕ якщо воно робить маскування
 * суворішим (або якщо маскування ще не було). Саме тому вкладена секція
 * ніколи не послаблює зовнішню. */
static inline void __set_BASEPRI_MAX(uint32_t basepri)
{
    __asm volatile("MSR basepri_max, %0" ::"r"(basepri) : "memory");
}
#endif /* CORTEXM_HAS_BASEPRI */

#if CORTEXM_HAS_EXCLUSIVE
static inline uint32_t __LDREXW(volatile uint32_t *addr)
{
    uint32_t value;
    __asm volatile("LDREX %0, [%1]" : "=r"(value) : "r"(addr) : "memory");
    return value;
}

/* Повертає 0 — запис відбувся; 1 — монітор було збито, запису НЕ сталося. */
static inline uint32_t __STREXW(uint32_t value, volatile uint32_t *addr)
{
    uint32_t status;
    __asm volatile("STREX %0, %2, [%1]" : "=&r"(status) : "r"(addr), "r"(value) : "memory");
    return status;
}

/* Знімає монітор, коли транзакцію кинуто на півдорозі. */
static inline void __CLREX(void) { __asm volatile("CLREX" ::: "memory"); }
#endif /* CORTEXM_HAS_EXCLUSIVE */

#endif /* __CMSIS_GCC_H */

#endif /* CORTEXM_H */
