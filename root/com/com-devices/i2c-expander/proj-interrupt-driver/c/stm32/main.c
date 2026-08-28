#include "stm32f4xx_hal.h"
#include <stdbool.h>

extern I2C_HandleTypeDef hi2c1;
#define MCP23017_ADDR_8BIT (0x20 << 1)

static volatile bool g_expander_int_pending = false;
static uint32_t g_last_int_tick = 0;

/* Обробник зовнішнього переривання EXTI (підключений до лінії /INT розширювача) */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_0) {
        uint32_t now = HAL_GetTick();
        /* Фільтрація брязкоту контактів: ігноруємо повторні імпульси швидше 30 мс */
        if ((now - g_last_int_tick) > 30) {
            g_expander_int_pending = true;
            g_last_int_tick = now;
        }
    }
}

void Process_Expander_Events(void) {
    if (!g_expander_int_pending) return;
    g_expander_int_pending = false;

    uint8_t intf[2] = {0};
    uint8_t intcap[2] = {0};

    /* Читання прапорців переривань */
    if (HAL_I2C_Mem_Read(&hi2c1, MCP23017_ADDR_8BIT, 0x0E, I2C_MEMADD_SIZE_8BIT, intf, 2, 100) == HAL_OK) {
        uint16_t active_pins = (uint16_t)intf[0] | ((uint16_t)intf[1] << 8);

        /* Читання зафіксованого стану (скидає /INT на MCP23017) */
        if (HAL_I2C_Mem_Read(&hi2c1, MCP23017_ADDR_8BIT, 0x10, I2C_MEMADD_SIZE_8BIT, intcap, 2, 100) == HAL_OK) {
            uint16_t pin_levels = (uint16_t)intcap[0] | ((uint16_t)intcap[1] << 8);

            for (uint8_t pin = 0; pin < 16; ++pin) {
                if (active_pins & (1 << pin)) {
                    bool level = (pin_levels & (1 << pin)) != 0;
                    /* Обробка натискання кнопки чи спрацьовування датчика */
                }
            }
        }
    }
}
