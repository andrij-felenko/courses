#include <stdbool.h>
#include "stm32f4xx_hal.h"

#define BTN_PORT     GPIOA
#define BTN_PIN      GPIO_PIN_0    // кнопка між ніжкою і землею
#define RELAY_PORT   GPIOB
#define RELAY_PIN    GPIO_PIN_5
#define DEBOUNCE_MS  25u           // «тиша» довша за деренчання (кілька мс)

static const bool ACTIVE_LOW = true;
static inline void relay_write(bool on) {
    HAL_GPIO_WritePin(RELAY_PORT, RELAY_PIN,
                      (on ^ ACTIVE_LOW) ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    relay_write(false);
    GPIO_InitTypeDef out = { .Pin = RELAY_PIN, .Mode = GPIO_MODE_OUTPUT_PP,
                             .Pull = GPIO_NOPULL, .Speed = GPIO_SPEED_FREQ_LOW };
    HAL_GPIO_Init(RELAY_PORT, &out);
    GPIO_InitTypeDef in  = { .Pin = BTN_PIN, .Mode = GPIO_MODE_INPUT,
                             .Pull = GPIO_PULLUP };   // спокій = 1, натиск тягне в 0
    HAL_GPIO_Init(BTN_PORT, &in);

    bool     relay_state  = false;  // логічний стан реле, який перемикаємо
    bool     last_reading = true;   // попереднє СИРЕ читання кнопки
    bool     btn_stable   = true;   // стан, у який кнопка вже устоялась
    uint32_t last_edge    = 0;      // коли сире читання востаннє смикнулось

    while (1) {
        bool reading = (HAL_GPIO_ReadPin(BTN_PORT, BTN_PIN) == GPIO_PIN_SET);

        if (reading != last_reading) {        // смикнулось — перезапуск відліку
            last_edge = HAL_GetTick();
            last_reading = reading;
        }

        if ((HAL_GetTick() - last_edge) > DEBOUNCE_MS && reading != btn_stable) {
            btn_stable = reading;
            if (!btn_stable) {                // саме натиск (не відпускання)
                relay_state = !relay_state;
                relay_write(relay_state);
            }
        }
    }
}
