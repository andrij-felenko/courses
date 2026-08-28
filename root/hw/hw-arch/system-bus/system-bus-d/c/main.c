#include <stdint.h>

// Адреси регістрів — це просто позиції пристрою в мапі пам'яті шини.
#define GPIO_MODE (*(volatile uint32_t *)0x40020000u)
#define GPIO_OUT  (*(volatile uint32_t *)0x40020014u)

void led_on(void) {
    GPIO_MODE = 0x1u;          // запис на шину: адреса 0x40020000, дані 1, "пишу"
    GPIO_OUT |= (1u << 5);     // читання-модифікація-запис того самого регістра
}

uint32_t read_out(void) {
    return GPIO_OUT;           // цикл читання: адреса 0x40020014, дані назад у ядро
}
