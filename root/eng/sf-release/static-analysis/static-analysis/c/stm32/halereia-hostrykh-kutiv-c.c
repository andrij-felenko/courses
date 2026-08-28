#include "main.h"

// (а) = замість ==
GPIO_PinState flag = GPIO_PIN_RESET;
if (flag = HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0)) {  // пастка: присвоєння, не порівняння
    printf("triggered\r\n");                       // виконується завжди, коли не RESET
}

// (б) звуження типу — маска нульова
uint8_t mask = 1 << 9;                 // 1<<9 = 512 = 0x200 (GPIO_PIN_9); uint8_t → 0
GPIO_InitTypeDef init = {0};
init.Pin = mask;                       // 0 — HAL_GPIO_Init не чіпає жодної ніжки
init.Mode = GPIO_MODE_OUTPUT_PP;
init.Pull = GPIO_NOPULL;
HAL_GPIO_Init(GPIOA, &init);           // мовчки не робить нічого
