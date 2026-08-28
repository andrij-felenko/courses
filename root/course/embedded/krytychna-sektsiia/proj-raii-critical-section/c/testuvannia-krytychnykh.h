#ifndef MOCK_CMSIS_COMPILER_H
#define MOCK_CMSIS_COMPILER_H

#include <stdint.h>
#include <stdbool.h>

/* Глобальні лічильники викликів для перевірки у тестах */
extern uint32_t g_mock_primask_state;
extern uint32_t g_mock_disable_irq_calls;
extern uint32_t g_mock_enable_irq_calls;

static inline uint32_t __get_PRIMASK(void) {
    return g_mock_primask_state;
}

static inline void __set_PRIMASK(uint32_t state) {
    g_mock_primask_state = state;
}

static inline void __disable_irq(void) {
    g_mock_disable_irq_calls++;
    g_mock_primask_state = 1U;
}

static inline void __enable_irq(void) {
    g_mock_enable_irq_calls++;
    g_mock_primask_state = 0U;
}

static inline uint32_t __get_IPSR(void) {
    return 0U; // Емуляція Thread Mode
}

#endif /* MOCK_CMSIS_COMPILER_H */
