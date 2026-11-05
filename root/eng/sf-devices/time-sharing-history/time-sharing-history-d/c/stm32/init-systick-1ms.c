#include "stm32f4xx.h"
#include <stdint.h>

// Прапорці квантів часу для двох обчислювальних задач
volatile uint32_t g_task_ticks = 0;
volatile uint8_t g_current_task = 0;

// Обробник системного таймерного переривання SysTick
void SysTick_Handler(void) {
    g_task_ticks++;
    
    // Кожні 5 мілісекунд (5 тіків) змінюємо активну задачу
    if (g_task_ticks >= 5) {
        g_task_ticks = 0;
        g_current_task = (g_current_task == 0) ? 1 : 0; // Квантування часу (Time Slicing)
    }
}

void init_systick_1ms(uint32_t cpu_freq_hz) {
    // Налаштування SysTick на генерування переривання кожну 1 мс
    SysTick->LOAD = (cpu_freq_hz / 1000) - 1;
    SysTick->VAL  = 0;
    SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk |
                    SysTick_CTRL_TICKINT_Msk   |
                    SysTick_CTRL_ENABLE_Msk;
}

void task_alpha_step(void) {
    // Частина обчислень Задачі A
}

void task_beta_step(void) {
    // Частина обчислень Задачі B (наприклад, опитування UART)
}

int main(void) {
    init_systick_1ms(16000000); // Тактування 16 МГц

    while (1) {
        // Простий квантований розподіл виконання на основі апаратного тика
        if (g_current_task == 0) {
            task_alpha_step();
        } else {
            task_beta_step();
        }
    }
}
