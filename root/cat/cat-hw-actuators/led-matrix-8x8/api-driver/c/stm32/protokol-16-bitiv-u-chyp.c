#include "stm32f1xx_hal.h"

#define DIN_PORT  GPIOA
#define DIN_PIN   GPIO_PIN_7    // дані в MAX7219
#define CLK_PORT  GPIOA
#define CLK_PIN   GPIO_PIN_5    // такт
#define LOAD_PORT GPIOA
#define LOAD_PIN  GPIO_PIN_4    // завантаження (CS)

// Надіслати один 16-бітний кадр: адреса реєстра + байт даних.
void max7219send(uint8_t addr, uint8_t data) {
    uint16_t frame16 = ((uint16_t)addr << 8) | data;   // старший байт = адреса
    HAL_GPIO_WritePin(LOAD_PORT, LOAD_PIN, GPIO_PIN_RESET);   // почали кадр
    for (int8_t i = 15; i >= 0; i--) {                        // старшим бітом уперед
        HAL_GPIO_WritePin(CLK_PORT, CLK_PIN, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(DIN_PORT, DIN_PIN,
                          ((frame16 >> i) & 1) ? GPIO_PIN_SET : GPIO_PIN_RESET);
        HAL_GPIO_WritePin(CLK_PORT, CLK_PIN, GPIO_PIN_SET);   // фронт CLK → біт зчитано
    }
    HAL_GPIO_WritePin(LOAD_PORT, LOAD_PIN, GPIO_PIN_SET);     // фронт LOAD → у реєстр
}
