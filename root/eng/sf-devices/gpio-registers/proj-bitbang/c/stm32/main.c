#include "stm32f4xx_hal.h"

#define PORT      GPIOB
#define PIN_DATA  GPIO_PIN_5
#define PIN_CLK   GPIO_PIN_6

void send_byte_slow(uint8_t b) {        // старший біт першим
    for (int i = 7; i >= 0; i--) {
        HAL_GPIO_WritePin(PORT, PIN_DATA,        // виставити поточний біт
                          ((b >> i) & 1) ? GPIO_PIN_SET : GPIO_PIN_RESET);
        HAL_GPIO_WritePin(PORT, PIN_CLK, GPIO_PIN_SET);   // фронт — приймач читає
        HAL_GPIO_WritePin(PORT, PIN_CLK, GPIO_PIN_RESET);
    }
}
