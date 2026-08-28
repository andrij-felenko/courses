#include "stm32f1xx_hal.h"
// HAL_Delay() має крок 1 мс — для 1 і 50 мкс потрібен свій delay_us()
// на лічильнику DWT->CYCCNT або на вільному таймері.

// Виставити один напівбайт (молодші 4 біти value) на лінії D4–D7
static void put_nibble(uint8_t value) {
    for (int i = 0; i < 4; i++)
        HAL_GPIO_WritePin(LCD_D_PORT[i], LCD_D_PIN[i],
                          ((value >> i) & 1) ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

// Клацнути строб: підняти E, витримати, опустити — на спаді контролер читає лінії
static void pulse_e(void) {
    HAL_GPIO_WritePin(LCD_E_PORT, LCD_E_PIN, GPIO_PIN_SET);
    delay_us(1);               // тримаємо E високим ≥ 0.45 мкс (беремо із запасом)
    HAL_GPIO_WritePin(LCD_E_PORT, LCD_E_PIN, GPIO_PIN_RESET);
    delay_us(50);              // даємо контролеру перетравити (звичайна команда ~37 мкс)
}
