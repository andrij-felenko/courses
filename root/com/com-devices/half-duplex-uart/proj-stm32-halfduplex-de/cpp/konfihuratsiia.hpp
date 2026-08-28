// Об'єктно-орієнтована ініціалізація USART1 у режимі Single-Wire Half-Duplex (C++)
#include <cstdint>

struct UsartSingleWireConfig {
    static constexpr void init(std::uint32_t baudrate, std::uint32_t pclk_hz) noexcept {
        // 1. Тактування GPIOA та USART1
        RCC->IOPENR |= RCC_IOPENR_GPIOAEN;
        RCC->APBENR2 |= RCC_APBENR2_USART1EN;

        // 2. Налаштування PA9 (TX): Alternate Function, Open-Drain, Pull-up
        GPIOA->MODER &= ~(GPIO_MODER_MODE9_Msk);
        GPIOA->MODER |= (0x02 << GPIO_MODER_MODE9_Pos);
        GPIOA->AFR[1] |= (0x01 << GPIO_AFRH_AFSEL9_Pos);
        GPIOA->OTYPER |= GPIO_OTYPER_OT9;
        GPIOA->PUPDR |= GPIO_PUPDR_PUPD9_0;
        GPIOA->OSPEEDR |= GPIO_OSPEEDR_OSPEED9;

        // 3. Налаштування бодрейту та режиму Half-Duplex
        USART1->CR1 = 0;
        USART1->BRR = (pclk_hz + (baudrate / 2)) / baudrate;
        USART1->CR3 |= USART_CR3_HDSEL;

        // 4. Увімкнення передавача, приймача та блоку USART
        USART1->CR1 |= (USART_CR1_TE | USART_CR1_RE | USART_CR1_UE);
    }
};
