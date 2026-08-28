#include <stdint.h>
#include <stdbool.h>

#define SRAM_MIN_ADDR  0x20000000U
#define SRAM_MAX_ADDR  0x20080000U

void execute_safe_boot_jump(uint32_t target_app_addr) {
    /* 1. Читання початкового MSP та точки входу */
    uint32_t app_msp = *(volatile uint32_t *)target_app_addr;
    uint32_t app_entry_addr = *(volatile uint32_t *)(target_app_addr + 4U);

    /* 2. Валідація стека та прапорця Thumb */
    if (app_msp < SRAM_MIN_ADDR || app_msp > SRAM_MAX_ADDR || (app_entry_addr & 1U) == 0U) {
        return; /* Образ некоректний, відхилити запуск */
    }

    /* 3. Глобальна зупинка переривань */
    __asm volatile ("cpsid i" : : : "memory");

    /* 4. Зупинка системного таймера SysTick */
    *(volatile uint32_t *)0xE000E010U = 0U; /* SysTick->CTRL */
    *(volatile uint32_t *)0xE000E018U = 0U; /* SysTick->VAL */

    /* 5. Очищення регістрів NVIC */
    volatile uint32_t *nvic_icer = (volatile uint32_t *)0xE000E180U;
    volatile uint32_t *nvic_icpr = (volatile uint32_t *)0xE000E280U;
    for (uint32_t i = 0; i < 8U; ++i) {
        nvic_icer[i] = 0xFFFFFFFFU;
        nvic_icpr[i] = 0xFFFFFFFFU;
    }

    /* 6. Релокація таблиці векторів у SCB */
    *(volatile uint32_t *)0xE000ED08U = target_app_addr; /* SCB->VTOR */

    __asm volatile ("dsb\n\tisb" : : : "memory");

    /* 7. Завантаження MSP та виклик Reset_Handler */
    __asm volatile ("msr msp, %0" : : "r" (app_msp) : "memory");

    void (*app_reset_handler)(void) = (void (*)(void))app_entry_addr;
    app_reset_handler();

    while (1) {} /* Сюди процесор ніколи не повертається */
}
