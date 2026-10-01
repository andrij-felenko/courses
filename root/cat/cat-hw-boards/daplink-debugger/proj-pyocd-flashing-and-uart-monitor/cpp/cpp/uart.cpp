#include "uart.hpp"

namespace mcu {

// Допоміжна адресація регістрів тактування (RCC) та портів GPIO для STM32 Cortex-M
struct RccRegisters {
    volatile uint32_t CR;
    volatile uint32_t PLLCFGR;
    volatile uint32_t CFGR;
    volatile uint32_t CIR;
    volatile uint32_t AHB1ENR; ///< Вмикання тактування GPIO (GPIOA = bit 0)
    volatile uint32_t AHB2ENR;
    volatile uint32_t AHB3ENR;
    uint32_t RESERVED0;
    volatile uint32_t APB1ENR; ///< Вмикання тактування USART2 (bit 17)
    volatile uint32_t APB2ENR; ///< Вмикання тактування USART1 (bit 4)
};

struct GpioRegisters {
    volatile uint32_t MODER;   ///< Режим роботи виводів (01: Output, 10: Alternate Function)
    volatile uint32_t OTYPER;  ///< Тип виходу (0: Push-Pull)
    volatile uint32_t OSPEEDR; ///< Швидкість роботи виводів
    volatile uint32_t PUPDR;   ///< Підтягуючі резистори (Pull-up / Pull-down)
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];  ///< Вибір альтернативної функції (AFR[0] для PIN0..7, AFR[1] для PIN8..15)
};

// Базові адреси периферії для STM32F4 (або аналогічного ARM Cortex-M МК)
constexpr uintptr_t RCC_BASE   = 0x40023800U;
constexpr uintptr_t GPIOA_BASE = 0x40020000U;

Uart::Uart(Registers* instance) noexcept
    : m_usart(instance) {}

void Uart::init(uint32_t pclk_freq, uint32_t baud_rate) noexcept {
    if (!m_usart || baud_rate == 0 || pclk_freq == 0) {
        return;
    }

    auto* rcc   = reinterpret_cast<RccRegisters*>(RCC_BASE);
    auto* gpioa = reinterpret_cast<GpioRegisters*>(GPIOA_BASE);

    // 1. Увімкнення тактування GPIOA та модуля USART2 через RCC
    rcc->AHB1ENR |= (1U << 0);  // GPIOAEN
    rcc->APB1ENR |= (1U << 17); // USART2EN

    // 2. Налаштування виводів GPIOA: PA2 (TX) та PA3 (RX) у режим альтернативної функції (AF7 для USART2)
    gpioa->MODER &= ~((3U << (2 * 2)) | (3U << (2 * 3)));
    gpioa->MODER |=  ((2U << (2 * 2)) | (2U << (2 * 3)));

    // Призначення альтернативної функції AF7 (0x07) для PA2 та PA3 у регістрі AFR[0]
    gpioa->AFR[0] &= ~((0xFU << (4 * 2)) | (0xFU << (4 * 3)));
    gpioa->AFR[0] |=  ((7U    << (4 * 2)) | (7U    << (4 * 3)));

    // Висока швидкість фронтів виводів (OSPEEDR)
    gpioa->OSPEEDR |= ((3U << (2 * 2)) | (3U << (2 * 3)));

    // 3. Розрахунок дільника BRR для встановлення швидкості (baud rate)
    // Формула: BRR = (PCLK + (Baud / 2)) / Baud для заокруглення до найближчого цілого
    uint32_t usart_div = (pclk_freq + (baud_rate / 2U)) / baud_rate;
    m_usart->BRR = usart_div;

    // 4. Скидання конфігураційного регістру CR1 та вмикання передавача (TE), приймача (RE) та модуля (UE)
    m_usart->CR1 = CR1_UE | CR1_TE | CR1_RE;
}

void Uart::write_char(char ch) noexcept {
    // Очікування, поки буфер передачі (TXE) звільниться від попереднього байта
    while (!(m_usart->SR & SR_TXE)) {
        // Очікування готовності апаратного буфера
    }

    // Запис символу у регістр даних DR для запуску передачі
    m_usart->DR = static_cast<uint8_t>(ch);
}

void Uart::write(std::string_view str) noexcept {
    for (char c : str) {
        write_char(c);
    }
}

void Uart::println(std::string_view str) noexcept {
    write(str);
    write_char('\r');
    write_char('\n');
}

void Uart::flush() noexcept {
    // Очікування повного завершення відправки останнього біта в лінію TX (прапорець TC)
    while (!(m_usart->SR & SR_TC)) {
        // Пасивне очікування фіналу передачі кадрів
    }
}

} // namespace mcu
