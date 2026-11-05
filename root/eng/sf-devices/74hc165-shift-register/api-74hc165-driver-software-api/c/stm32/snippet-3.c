#include "stm32f4xx_hal.h"
#include <stdint.h>

// Структура для конфігурації драйвера 74HC165
typedef struct {
    GPIO_TypeDef* port_sh_ld;
    uint16_t pin_sh_ld;
    GPIO_TypeDef* port_clk;
    uint16_t pin_clk;
    GPIO_TypeDef* port_data;
    uint16_t pin_data;
} HC165_Config;

// Ініціалізація пінів
void HC165_Init(const HC165_Config* config) {
    // Припускаємо, що тактування портів увімкнено на вищому рівні
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    // Налаштування виходів (SH/LD та CLK)
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    
    GPIO_InitStruct.Pin = config->pin_sh_ld;
    HAL_GPIO_Init(config->port_sh_ld, &GPIO_InitStruct);
    
    GPIO_InitStruct.Pin = config->pin_clk;
    HAL_GPIO_Init(config->port_clk, &GPIO_InitStruct);

    // Налаштування входу (DATA)
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    GPIO_InitStruct.Pin = config->pin_data;
    HAL_GPIO_Init(config->port_data, &GPIO_InitStruct);

    // Встановлення початкових станів
    HAL_GPIO_WritePin(config->port_sh_ld, config->pin_sh_ld, GPIO_PIN_SET);
    HAL_GPIO_WritePin(config->port_clk, config->pin_clk, GPIO_PIN_RESET);
}

// Зчитування 8 біт даних з регістра
uint8_t HC165_Read(const HC165_Config* config) {
    uint8_t incoming_data = 0;

    // Захоплення даних (SH/LD = 0, потім SH/LD = 1)
    __disable_irq(); // Початок критичної секції
    
    HAL_GPIO_WritePin(config->port_sh_ld, config->pin_sh_ld, GPIO_PIN_RESET);
    // Невелика затримка (зазвичай кілька наносекунд, інструкції достатньо)
    __ASM volatile ("nop"); 
    HAL_GPIO_WritePin(config->port_sh_ld, config->pin_sh_ld, GPIO_PIN_SET);

    // Зчитування 8 біт (від старшого до молодшого)
    for (int i = 7; i >= 0; i--) {
        // Зчитуємо поточний біт
        if (HAL_GPIO_ReadPin(config->port_data, config->pin_data) == GPIO_PIN_SET) {
            incoming_data |= (1 << i);
        }

        // Генеруємо тактовий імпульс CLK (0 -> 1 -> 0)
        HAL_GPIO_WritePin(config->port_clk, config->pin_clk, GPIO_PIN_SET);
        __ASM volatile ("nop");
        HAL_GPIO_WritePin(config->port_clk, config->pin_clk, GPIO_PIN_RESET);
    }
    
    __enable_irq(); // Кінець критичної секції

    return incoming_data;
}
