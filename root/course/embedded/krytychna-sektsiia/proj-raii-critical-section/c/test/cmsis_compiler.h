#ifndef MOCK_CMSIS_COMPILER_H
#define MOCK_CMSIS_COMPILER_H

/*
 * Заглушка CMSIS для хостових тестів (x86_64).
 *
 * Складається так: gcc -Ic/test -Ic ... — і драйвер бачить цей файл замість
 * справжнього cmsis_compiler.h, нічого про підміну не знаючи. Інструкцій
 * CPSID/MRS/MSR на хості немає, тому стан регістрів тримаємо в структурі.
 *
 * Стан оголошено static: тест — одна одиниця трансляції, і зайвий .c тут
 * лише додав би файлів.
 */

#include <stdbool.h>
#include <stdint.h>

/* Емулюємо ядро з BASEPRI (Cortex-M4), щоб перевірити й пріоритетну секцію. */
#define CS_HAS_BASEPRI 1

typedef struct {
    uint32_t primask;
    uint32_t basepri;
    uint32_t ipsr;            /* != 0 — вдаємо контекст переривання */
    uint32_t disable_calls;   /* скільки разів заходили */
    uint32_t restore_calls;   /* скільки разів виходили */
    uint32_t depth;           /* поточна глибина вкладення */
    uint32_t max_depth;
} cmsis_mock_t;

static cmsis_mock_t g_mock;

static inline void cmsis_mock_reset(void)
{
    const cmsis_mock_t clean = { 0U, 0U, 0U, 0U, 0U, 0U, 0U };
    g_mock = clean;
}

static inline uint32_t __get_PRIMASK(void)
{
    return g_mock.primask;
}

static inline void __set_PRIMASK(uint32_t value)
{
    g_mock.restore_calls++;
    if (g_mock.depth > 0U) {
        g_mock.depth--;
    }
    g_mock.primask = value;
}

static inline void __disable_irq(void)
{
    g_mock.disable_calls++;
    g_mock.depth++;
    if (g_mock.depth > g_mock.max_depth) {
        g_mock.max_depth = g_mock.depth;
    }
    g_mock.primask = 1U;
}

static inline void __enable_irq(void)
{
    g_mock.primask = 0U;
}

static inline uint32_t __get_BASEPRI(void)
{
    return g_mock.basepri;
}

static inline void __set_BASEPRI(uint32_t value)
{
    g_mock.basepri = value;
}

static inline void __set_BASEPRI_MAX(uint32_t value)
{
    /*
     * Апаратна семантика: менше число — вищий пріоритет, тобто суворіше
     * маскування; нуль означає «не маскуємо». Запис відбувається лише тоді,
     * коли поріг посилюється.
     */
    if (value != 0U && (g_mock.basepri == 0U || value < g_mock.basepri)) {
        g_mock.basepri = value;
    }
}

static inline uint32_t __get_IPSR(void)
{
    return g_mock.ipsr;
}

static inline void __NOP(void)  { }
static inline void __DSB(void)  { }
static inline void __ISB(void)  { }

#define __BKPT(value) ((void)(value))

#endif /* MOCK_CMSIS_COMPILER_H */
