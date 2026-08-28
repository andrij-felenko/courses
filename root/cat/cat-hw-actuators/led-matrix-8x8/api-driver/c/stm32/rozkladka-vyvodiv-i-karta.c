#include "stm32f1xx_hal.h"

// На STM32 вивід — це пара «порт + маска ніжки», тож тримаємо її структурою.
typedef struct { GPIO_TypeDef *port; uint16_t pin; } pin_t;

// Стовпці 0..7 (катоди через резистори).
static const pin_t COL_PIN[8] = {
    {GPIOA, GPIO_PIN_0}, {GPIOA, GPIO_PIN_1}, {GPIOA, GPIO_PIN_2}, {GPIOA, GPIO_PIN_3},
    {GPIOA, GPIO_PIN_4}, {GPIOA, GPIO_PIN_5}, {GPIOA, GPIO_PIN_6}, {GPIOA, GPIO_PIN_7},
};

// Рядкові ключі 0..7 (аноди до +5 В). PB2 обходимо — це BOOT1.
static const pin_t ROW_PIN[8] = {
    {GPIOB, GPIO_PIN_0}, {GPIOB, GPIO_PIN_1}, {GPIOB, GPIO_PIN_3}, {GPIOB, GPIO_PIN_4},
    {GPIOB, GPIO_PIN_5}, {GPIOB, GPIO_PIN_6}, {GPIOB, GPIO_PIN_7}, {GPIOB, GPIO_PIN_8},
};
