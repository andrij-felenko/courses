#include <stdint.h>
#include <stdbool.h>

#define APP_START_ADDRESS 0x08008000UL

static inline void cpu_disable_irq(void)  { __asm__ volatile ("cpsid i" : : : "memory"); }
static inline void cpu_set_msp(uint32_t val) { __asm__ volatile ("msr msp, %0" : : "r" (val) : "memory"); }
static inline void cpu_dsb(void)          { __asm__ volatile ("dsb 0xF" : : : "memory"); }
static inline void cpu_isb(void)          { __asm__ volatile ("isb 0xF" : : : "memory"); }

typedef void (*app_entry_fn)(void);

bool bootloader_verify_and_jump(uint32_t app_addr) {
    uint32_t app_stack = *(volatile uint32_t*)app_addr;
    uint32_t app_reset = *(volatile uint32_t*)(app_addr + 4);

    /* 1. Базова перевірка валідності стека (чи потрапляє в SRAM 0x20000000..0x20040000) */
    if ((app_stack < 0x20000000UL) || (app_stack > 0x20040000UL)) {
        return false;
    }

    /* 2. Перевірка валідності адреси точки входу (повинна бути у Flash та мати біт Thumb=1) */
    if ((app_reset < app_addr) || (app_reset > 0x08080000UL) || ((app_reset & 1UL) == 0)) {
        return false;
    }

    /* 3. Глобальне блокування переривань */
    cpu_disable_irq();

    /* 4. Зупинка системного таймера SysTick */
    volatile uint32_t *systick_ctrl = (volatile uint32_t*)0xE000E010;
    volatile uint32_t *systick_load = (volatile uint32_t*)0xE000E014;
    volatile uint32_t *systick_val  = (volatile uint32_t*)0xE000E018;
    *systick_ctrl = 0;
    *systick_load = 0;
    *systick_val  = 0;

    /* 5. Очищення та вимкнення всіх ліній NVIC */
    volatile uint32_t *nvic_icer = (volatile uint32_t*)0xE000E180;
    volatile uint32_t *nvic_icpr = (volatile uint32_t*)0xE000E280;
    for (int i = 0; i < 8; ++i) {
        nvic_icer[i] = 0xFFFFFFFFUL;
        nvic_icpr[i] = 0xFFFFFFFFUL;
    }

    /* 6. Релокація VTOR */
    volatile uint32_t *scb_vtor = (volatile uint32_t*)0xE000ED08;
    *scb_vtor = app_addr;

    /* 7. Бар'єри конвеєра */
    cpu_dsb();
    cpu_isb();

    /* 8. Ініціалізація MSP додатку */
    cpu_set_msp(app_stack);

    /* 9. Перехід у Reset_Handler */
    app_entry_fn jump_to_app = (app_entry_fn)app_reset;
    jump_to_app();

    return true; /* Недосяжний код */
}
