#include <stdint.h>

/* Безпечна критична секція на C для ARM Cortex-M */
static inline uint32_t critical_section_enter(void) {
    uint32_t primask;
    /* Зчитуємо поточний стан регістра PRIMASK */
    __asm volatile ("MRS %0, primask" : "=r" (primask) :: "memory");
    /* Вимикаємо переривання */
    __asm volatile ("CPSID i" ::: "memory");
    return primask;
}

static inline void critical_section_exit(uint32_t primask) {
    /* Відновлюємо саме той стан, який був до входу */
    __asm volatile ("MSR primask, %0" :: "r" (primask) : "memory");
}

/* Приклад безпечного оновлення 64-бітного таймера */
volatile uint64_t g_system_ticks = 0;

uint64_t get_system_ticks_safe(void) {
    uint32_t state = critical_section_enter();
    uint64_t ticks = g_system_ticks;
    critical_section_exit(state);
    return ticks;
}
