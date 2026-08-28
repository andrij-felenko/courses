#include <stdint.h>
#include <stdbool.h>

#if defined(PLATFORM_ESP32)
    #include <Arduino.h>
#elif defined(PLATFORM_STM32)
    #include "stm32f4xx_hal.h"
#endif

// Структура конфігурації світлодіода
typedef struct {
    uint8_t pin;
    bool is_active_high;
} led_controller_t;

void led_init(led_controller_t *dev, uint8_t pin, bool active_high) {
    if (!dev) return;
    dev->pin = pin;
    dev->is_active_high = active_high;

#if defined(PLATFORM_ESP32)
    pinMode(dev->pin, OUTPUT);
    digitalWrite(dev->pin, dev->is_active_high ? LOW : HIGH);
#elif defined(PLATFORM_STM32)
    __HAL_RCC_GPIOA_CLK_ENABLE();
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = (1 << dev->pin);
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &gpio);
    HAL_GPIO_WritePin(GPIOA, (uint16_t)(1 << dev->pin), 
                      dev->is_active_high ? GPIO_PIN_RESET : GPIO_PIN_SET);
#endif
}

void led_set_state(const led_controller_t *dev, bool state) {
    if (!dev) return;
    bool level = dev->is_active_high ? state : !state;

#if defined(PLATFORM_ESP32)
    digitalWrite(dev->pin, level ? HIGH : LOW);
#elif defined(PLATFORM_STM32)
    HAL_GPIO_WritePin(GPIOA, (uint16_t)(1 << dev->pin), 
                      level ? GPIO_PIN_SET : GPIO_PIN_RESET);
#endif
}
