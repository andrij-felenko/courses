// main.c — користувацький сильний обробник переривання
#include <stdint.h>

volatile uint32_t g_system_ticks = 0;

// Звичайне (сильне) визначення: STB_GLOBAL
void SysTick_Handler(void)
{
    g_system_ticks++;
}
