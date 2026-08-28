// Регістрова ініціалізація USART1 у режимі Single-Wire Half-Duplex (STM32, C)
void usart1_half_duplex_init(uint32_t baudrate, uint32_t pclk_hz) {
    // 1. Тактування GPIOA та USART1
    RCC->IOPENR |= RCC_IOPENR_GPIOAEN;
    RCC->APBENR2 |= RCC_APBENR2_USART1EN;

    // 2. Налаштування піна PA9 (USART1_TX): Alternate Function, Open-Drain, Pull-up, High Speed
    GPIOA->MODER &= ~(GPIO_MODER_MODE9_Msk);
    GPIOA->MODER |= (0x02 << GPIO_MODER_MODE9_Pos);      // AF mode
    GPIOA->AFR[1] |= (0x01 << GPIO_AFRH_AFSEL9_Pos);      // AF1 = USART1
    GPIOA->OTYPER |= GPIO_OTYPER_OT9;                    // Open-Drain (обов'язково!)
    GPIOA->PUPDR |= GPIO_PUPDR_PUPD9_0;                  // Внутрішня підтяжка Pull-up
    GPIOA->OSPEEDR |= GPIO_OSPEEDR_OSPEED9;              // High speed

    // 3. Налаштування USART1
    USART1->CR1 = 0;                                     // Вимкнення перед конфігурацією
    USART1->BRR = (pclk_hz + (baudrate / 2)) / baudrate; // Розрахунок подільника частоти

    // 4. Увімкнення режиму Half-Duplex
    USART1->CR3 |= USART_CR3_HDSEL;

    // 5. Увімкнення передавача та приймача
    USART1->CR1 |= (USART_CR1_TE | USART_CR1_RE | USART_CR1_UE);
}
