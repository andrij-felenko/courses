#include <stdint.h>

/* Визначення регістру PRIMASK для архітектури ARM Cortex-M */
static inline uint32_t __get_PRIMASK(void) {
    uint32_t result;
    __asm volatile ("MRS %0, primask" : "=r" (result) :: "memory");
    return result;
}

static inline void __disable_irq(void) {
    __asm volatile ("cpsid i" : : : "memory");
}

static inline void __set_PRIMASK(uint32_t priMask) {
    __asm volatile ("MSR primask, %0" : : "r" (priMask) : "memory");
}

/* Спільний ресурс між ISR та головним циклом */
static volatile uint32_t system_ticks = 0;

/* Низькорівневий захист критичної секції у Bare-Metal */
uint32_t safe_read_and_reset_ticks(void) {
    /* 1. Збереження попереднього стану переривань */
    uint32_t state = __get_PRIMASK();
    
    /* 2. Апаратне маскування переривань */
    __disable_irq();

    /* 3. Критична секція: неподільна робота зі спільним станом */
    uint32_t current = system_ticks;
    system_ticks = 0;

    /* 4. Відновлення попереднього стану (а не безумовне ввімкнення) */
    __set_PRIMASK(state);

    return current;
}
