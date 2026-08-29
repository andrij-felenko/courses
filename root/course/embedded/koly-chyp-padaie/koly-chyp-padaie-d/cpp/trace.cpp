#include "trace.hpp"

#include "stm32f4xx.h"

namespace trace {
namespace {

// USART2 живиться від APB1; для типової конфігурації STM32F4 на 168 МГц це 42 МГц.
constexpr std::uint32_t kApb1Hz = 42'000'000U;
constexpr std::uint32_t kBaud   = 115'200U;

// Стеля очікування замість while(!TXE): якщо тактування USART зникло разом із
// рештою системи, нескінченний цикл перетворив би звіт на друге зависання.
constexpr std::uint32_t kSpinLimit = 300'000U;

constexpr std::string_view kHexDigits{"0123456789ABCDEF"};

} // namespace

void Uart::init() noexcept
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;
    __DSB(); // дочекатися, доки запис у RCC дійде до шини

    // PA2 і PA3 — режим альтернативної функції (MODER = 0b10 на пін).
    GPIOA->MODER &= ~((3U << (2U * 2U)) | (3U << (3U * 2U)));
    GPIOA->MODER |= (2U << (2U * 2U)) | (2U << (3U * 2U));

    // AF7 = USART2, по чотири біти на пін.
    GPIOA->AFR[0] &= ~((0xFU << (2U * 4U)) | (0xFU << (3U * 4U)));
    GPIOA->AFR[0] |= (7U << (2U * 4U)) | (7U << (3U * 4U));

    USART2->BRR = (kApb1Hz + kBaud / 2U) / kBaud; // oversampling 16, округлення
    USART2->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;
    USART2->CR2 = 0U;
    USART2->CR3 = 0U;
}

void Uart::put(std::uint8_t byte) noexcept
{
    for (std::uint32_t spin = kSpinLimit; (USART2->SR & USART_SR_TXE) == 0U; --spin) {
        if (spin == 0U) {
            return; // лінія мертва — губимо байт, але не вішаємо чип
        }
    }
    USART2->DR = byte;
}

void Uart::write(std::string_view text) noexcept
{
    // string_view несе довжину із собою, тож обірваного рядка тут не буває.
    for (char symbol : text) {
        put(static_cast<std::uint8_t>(symbol));
    }
}

void Uart::write(char symbol) noexcept
{
    put(static_cast<std::uint8_t>(symbol));
}

void Uart::write(Hex value) noexcept
{
    write(std::string_view{"0x"});
    for (int shift = 28; shift >= 0; shift -= 4) {
        write(kHexDigits[(value.value >> shift) & 0xFU]);
    }
}

std::optional<char> Uart::read() noexcept
{
    if ((USART2->SR & USART_SR_RXNE) == 0U) {
        return std::nullopt;
    }
    return static_cast<char>(USART2->DR & 0xFFU);
}

void Uart::flush() noexcept
{
    for (std::uint32_t spin = kSpinLimit; (USART2->SR & USART_SR_TC) == 0U; --spin) {
        if (spin == 0U) {
            return;
        }
    }
}

} // namespace trace
