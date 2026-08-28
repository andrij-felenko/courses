#include "stm32f4xx_hal.h"

static GPIO_TypeDef* const PORTS[4] = {GPIOA, GPIOA, GPIOA, GPIOA};
static const uint16_t PINS[4] = {GPIO_PIN_0, GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3};

void hal_set_high(uint8_t pin) {
    GPIO_InitTypeDef g = {0};
    g.Pin = PINS[pin];
    g.Mode = GPIO_MODE_OUTPUT_PP;
    g.Pull = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(PORTS[pin], &g);
    HAL_GPIO_WritePin(PORTS[pin], PINS[pin], GPIO_PIN_SET);
}

void hal_set_low(uint8_t pin) {
    GPIO_InitTypeDef g = {0};
    g.Pin = PINS[pin];
    g.Mode = GPIO_MODE_OUTPUT_PP;
    g.Pull = GPIO_NOPULL;
    g.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(PORTS[pin], &g);
    HAL_GPIO_WritePin(PORTS[pin], PINS[pin], GPIO_PIN_RESET);
}

void hal_set_hiz(uint8_t pin) {
    GPIO_InitTypeDef g = {0};
    g.Pin = PINS[pin];
    g.Mode = GPIO_MODE_INPUT;
    g.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(PORTS[pin], &g);
}
