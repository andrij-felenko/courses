// itm_debug.c — Швидкий неблокуючий вивід через порт CoreSight ITM
#include <stdint.h>

#define ITM_TER         (*(volatile uint32_t *)0xE0000E00U) // ITM Trace Enable Register
#define ITM_TCR         (*(volatile uint32_t *)0xE0000E80U) // ITM Trace Control Register
#define ITM_PORT0_U8    (*(volatile uint8_t  *)0xE0000000U) // ITM Stimulus Port 0 (8-bit)
#define DEMCR           (*(volatile uint32_t *)0xE000EDFCU) // Debug Exception & Monitor Control

void itm_init(void) {
    // Вмикаємо трасування в модулі CoreSight
    DEMCR |= (1U << 24); // TRCENA bit
    ITM_TCR |= (1U << 0); // ITMENA bit
    ITM_TER |= (1U << 0); // Дозволяємо стимул-порт 0
}

void itm_putc(char ch) {
    // Перевіряємо, чи підключено відлагоджувач і чи дозволено порт ITM 0
    if ((DEMCR & (1U << 24)) && (ITM_TER & (1U << 0))) {
        // Чекаємо, доки апаратний буфер FIFO звільниться
        while (ITM_PORT0_U8 == 0) {
            __asm__ volatile ("nop");
        }
        ITM_PORT0_U8 = (uint8_t)ch;
    }
}

void itm_puts(const char *str) {
    while (*str) {
        itm_putc(*str++);
    }
}
