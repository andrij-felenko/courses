// (а) правильно: порівняння, не присвоєння
if (HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_0) == GPIO_PIN_SET) {
    printf("triggered\r\n");
}

// (б) правильно: тип тримає всю ширину маски
uint32_t mask32 = (1UL << 9);          // 0x200 == GPIO_PIN_9, поле Pin — 32-розрядне
GPIO_InitTypeDef init = {0};
init.Pin = mask32;
init.Mode = GPIO_MODE_OUTPUT_PP;
init.Pull = GPIO_NOPULL;
HAL_GPIO_Init(GPIOA, &init);

// або якщо потрібен саме uint8_t — біт має влазити (0..7, не 9):
uint8_t mask8 = (1U << 2);             // 0x04 — влазить у uint8_t
