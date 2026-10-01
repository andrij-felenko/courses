#include "uart.hpp"

namespace {

// Адресація регістрів периферії для мікроконтролерів серії ARM Cortex-M
constexpr uintptr_t PERIPH_BASE     = 0x40000000U;
constexpr uintptr_t APB2PERIPH_BASE = PERIPH_BASE + 0x00010000U;
constexpr uintptr_t AHBPERIPH_BASE  = PERIPH_BASE + 0x00020000U;

constexpr uintptr_t RCC_BASE        = AHBPERIPH_BASE + 0x00001000U;
constexpr uintptr_t GPIOA_BASE      = APB2PERIPH_BASE + 0x00000800U;
constexpr uintptr_t USART1_BASE     = APB2PERIPH_BASE + 0x00038000U;

struct RccRegs {
    volatile uint32_t CR;
    volatile uint32_t CFGR;
    volatile uint32_t CIR;
    volatile uint32_t APB2RSTR;
    volatile uint32_t APB1RSTR;
    volatile uint32_t AHBENR;
    volatile uint32_t APB2ENR;
    volatile uint32_t APB1ENR;
};

struct GpioRegs {
    volatile uint32_t CRL;
    volatile uint32_t CRH;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t BRR;
    volatile uint32_t LCKR;
};

struct UsartRegs {
    volatile uint32_t SR;
    volatile uint32_t DR;
    volatile uint32_t BRR;
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t CR3;
    volatile uint32_t GTPR;
};

auto* const RCC   = reinterpret_cast<RccRegs*>(RCC_BASE);
auto* const GPIOA = reinterpret_cast<GpioRegs*>(GPIOA_BASE);
auto* const USART = reinterpret_cast<UsartRegs*>(USART1_BASE);

constexpr uint32_t RCC_APB2ENR_IOPAEN   = (1U << 2);
constexpr uint32_t RCC_APB2ENR_USART1EN  = (1U << 14);

constexpr uint32_t USART_CR1_RE  = (1U << 2);
constexpr uint32_t USART_CR1_TE  = (1U << 3);
constexpr uint32_t USART_CR1_UE  = (1U << 13);

constexpr uint32_t USART_SR_RXNE = (1U << 5);
constexpr uint32_t USART_SR_TXE  = (1U << 7);

constexpr uint32_t SYSTEM_CLOCK_HZ = 72000000U;

} // namespace

namespace mcu {

Uart::Uart(BaudRate baud_rate) noexcept
    : baud_rate_(baud_rate), is_initialized_(false) {}

Uart::Uart(Uart&& other) noexcept
    : baud_rate_(other.baud_rate_), is_initialized_(other.is_initialized_) {
    other.is_initialized_ = false;
}

Uart& Uart::operator=(Uart&& other) noexcept {
    if (this != &other) {
        baud_rate_ = other.baud_rate_;
        is_initialized_ = other.is_initialized_;
        other.is_initialized_ = false;
    }
    return *this;
}

void Uart::init() {
    configure_hardware();
    is_initialized_ = true;
}

void Uart::configure_hardware() const {
    // 1. Ввімкнення тактування порту GPIOA та USART1
    RCC->APB2ENR |= (RCC_APB2ENR_IOPAEN | RCC_APB2ENR_USART1EN);

    // 2. Конфігурація виводів PA9 (TX AF Push-Pull) та PA10 (RX Input Floating)
    GPIOA->CRH &= ~(0xFFU << 4);
    GPIOA->CRH |= (0xBU << 4);  // PA9: Alternate Function Output Push-Pull 50MHz
    GPIOA->CRH |= (0x4U << 8);  // PA10: Floating Input

    // 3. Налаштування регістру ділення частоти BRR
    const uint32_t baud_val = static_cast<uint32_t>(baud_rate_);
    const uint32_t usartdiv = (SYSTEM_CLOCK_HZ + (baud_val / 2U)) / baud_val;
    USART->BRR = usartdiv;

    // 4. Увімкнення блоків TE, RE та модуля USART
    USART->CR1 = 0;
    USART->CR1 |= (USART_CR1_TE | USART_CR1_RE | USART_CR1_UE);
}

void Uart::send_char(char c) const {
    if (!is_initialized_) return;

    uint32_t timeout = 1000000U;
    while (!(USART->SR & USART_SR_TXE)) {
        if (--timeout == 0) return;
    }
    USART->DR = static_cast<uint8_t>(c);
}

void Uart::send_string(std::string_view str) const {
    for (char c : str) {
        send_char(c);
    }
}

void Uart::send_bytes(std::span<const uint8_t> data) const {
    for (uint8_t byte : data) {
        send_char(static_cast<char>(byte));
    }
}

bool Uart::receive_char(char& out_c) const {
    if (!is_initialized_) return false;

    if (USART->SR & USART_SR_RXNE) {
        out_c = static_cast<char>(USART->DR & 0xFFU);
        return true;
    }
    return false;
}

} // namespace mcu
