#include <stdint.h>
#include <stdbool.h>

static volatile uint32_t last_tick = 0;   // мітка часу останньої прийнятої події
extern uint32_t millis(void);             // системний лічильник мілісекунд

void EXTI0_IRQHandler(void) {
    if (EXTI->PR & (1u << 0)) {
        EXTI->PR = (1u << 0);              // зняти апаратний прапорець завжди
        uint32_t now = millis();
        if (now - last_tick >= 20) {      // 20 мс тиші між справжніми натисками
            last_tick = now;
            on_button_press();            // одне натискання -> один виклик
        }
        // інакше це брязкіт того самого натиску — мовчки ігноруємо
    }
}
