#include <stdint.h>

typedef void (*entry_fn)(void);

void boot_jump_to_app(uint32_t app_base) {
    __asm__ volatile ("cpsid i" : : : "memory");

    /* Зупинка SysTick */
    *(volatile uint32_t*)0xE000E010 = 0;

    /* Встановлення VTOR */
    *(volatile uint32_t*)0xE000ED08 = app_base;

    __asm__ volatile ("dsb 0xF" : : : "memory");
    __asm__ volatile ("isb 0xF" : : : "memory");

    /* Завантаження стека та перехід */
    uint32_t msp_val = *(volatile uint32_t*)app_base;
    uint32_t reset_val = *(volatile uint32_t*)(app_base + 4);

    __asm__ volatile ("msr msp, %0" : : "r" (msp_val) : "memory");
    ((entry_fn)reset_val)();
}
