#include <stdbool.h>
#include "stm32f4xx_hal.h"

#define RELAY_PORT  GPIOB
#define RELAY_PIN   GPIO_PIN_5
#define RELAY_ON    GPIO_PIN_RESET
#define RELAY_OFF   GPIO_PIN_SET

// Стан таймера реле.
static bool     relay_active = false;  // чи реле зараз увімкнене таймером
static uint32_t relay_off_at = 0;      // МИТЬ (за HAL_GetTick), коли треба вимкнути

// Увімкнути реле рівно на duration_ms мілісекунд.
void relay_on_for(uint32_t duration_ms) {
    HAL_GPIO_WritePin(RELAY_PORT, RELAY_PIN, RELAY_ON);
    relay_active = true;
    relay_off_at = HAL_GetTick() + duration_ms;   // коли гасити
}

// Викликати В КОЖНОМУ проході циклу: сам вимкне, коли час вийде.
void relay_tick(void) {
    // HAL_GetTick() — 32 біти, тож та сама поправка на переповнення, що й нижче.
    if (relay_active && (int32_t)(HAL_GetTick() - relay_off_at) >= 0) {
        HAL_GPIO_WritePin(RELAY_PORT, RELAY_PIN, RELAY_OFF);
        relay_active = false;
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    HAL_GPIO_WritePin(RELAY_PORT, RELAY_PIN, RELAY_OFF);
    GPIO_InitTypeDef gpio = { .Pin = RELAY_PIN, .Mode = GPIO_MODE_OUTPUT_PP,
                              .Pull = GPIO_NOPULL, .Speed = GPIO_SPEED_FREQ_LOW };
    HAL_GPIO_Init(RELAY_PORT, &gpio);
    relay_on_for(5000);               // клацнули увімкнене на 5 секунд

    while (1) {
        relay_tick();                 // стежить за часом, не блокуючи
        // ...сюди можна дописати будь-що: кнопки, давачі, індикатор —
        //    усе працює, поки реле відлічує свої 5 секунд.
    }
}
