#include <stdbool.h>
#include "stm32f4xx_hal.h"

#define RELAY_PORT  GPIOB
#define RELAY_PIN   GPIO_PIN_5

// Уся полярність модуля живе ТУТ, в одному місці.
static const bool ACTIVE_LOW = true;

static inline void relay_write(bool on) {
    // XOR з ACTIVE_LOW інвертує рівень лише коли модуль active-low.
    HAL_GPIO_WritePin(RELAY_PORT, RELAY_PIN,
                      (on ^ ACTIVE_LOW) ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

static inline void relay_on(void)  { relay_write(true);  }
static inline void relay_off(void) { relay_write(false); }

int main(void) {
    HAL_Init();
    SystemClock_Config();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    relay_off();                     // безпечний рівень СПЕРШУ (див. крок 1)
    GPIO_InitTypeDef gpio = { .Pin = RELAY_PIN, .Mode = GPIO_MODE_OUTPUT_PP,
                              .Pull = GPIO_NOPULL, .Speed = GPIO_SPEED_FREQ_LOW };
    HAL_GPIO_Init(RELAY_PORT, &gpio);

    while (1) {
        relay_on();
        HAL_Delay(1000);
        relay_off();
        HAL_Delay(1000);
    }
}
