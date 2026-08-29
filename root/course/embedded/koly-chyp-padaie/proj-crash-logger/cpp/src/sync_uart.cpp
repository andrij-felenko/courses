#include "sync_uart.hpp"

#include "stm32f4xx.h"

namespace io {
namespace {

// Скільки разів опитуємо TXE, перш ніж визнати передавач мертвим: в аварії
// краще загубити рядок звіту, ніж зависнути в обробнику назавжди.
constexpr std::uint32_t kSpinLimit = 2'000'000;

constexpr unsigned kTxPin = 9;  // PA9,  AF7
constexpr unsigned kRxPin = 10; // PA10, AF7
constexpr std::uint32_t kAlternateFn = 7;

TxResult put(char c) noexcept
{
    for (std::uint32_t spin = kSpinLimit; (USART1->SR & USART_SR_TXE) == 0; --spin) {
        if (spin == 0) {
            return std::unexpected(TxError::Timeout);
        }
    }
    USART1->DR = static_cast<std::uint32_t>(static_cast<std::uint8_t>(c));
    return {};
}

} // namespace

std::array<char, 10> to_hex(std::uint32_t value) noexcept
{
    constexpr std::string_view digits{"0123456789ABCDEF"};
    std::array<char, 10> out{'0', 'x'};
    for (unsigned i = 0; i < 8; ++i) {
        out[2 + i] = digits[(value >> ((7 - i) * 4)) & 0xFu];
    }
    return out;
}

namespace console {

void init(std::uint32_t pclk_hz, std::uint32_t baud) noexcept
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;

    const std::uint32_t mode_mask = (3u << (kTxPin * 2)) | (3u << (kRxPin * 2));
    GPIOA->MODER = (GPIOA->MODER & ~mode_mask) |
                   ((2u << (kTxPin * 2)) | (2u << (kRxPin * 2)));
    GPIOA->OSPEEDR |= mode_mask;

    const std::uint32_t af_mask =
        (0xFu << ((kTxPin - 8) * 4)) | (0xFu << ((kRxPin - 8) * 4));
    GPIOA->AFR[1] = (GPIOA->AFR[1] & ~af_mask) |
                    ((kAlternateFn << ((kTxPin - 8) * 4)) |
                     (kAlternateFn << ((kRxPin - 8) * 4)));

    USART1->BRR = (pclk_hz + baud / 2) / baud; // OVER8 = 0
    USART1->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;
}

TxResult write(std::string_view text) noexcept
{
    for (char c : text) {
        if (auto sent = put(c); !sent) {
            return sent;
        }
    }
    return {};
}

TxResult write_hex(std::uint32_t value) noexcept
{
    const auto text = to_hex(value);
    return write(std::string_view{text.data(), text.size()});
}

TxResult write_dec(std::uint32_t value) noexcept
{
    if (value == 0) {
        return write("0");
    }

    std::array<char, 10> buf{};
    std::size_t pos = buf.size();
    while (value > 0 && pos > 0) {
        buf[--pos] = static_cast<char>('0' + (value % 10));
        value /= 10;
    }
    return write(std::string_view{buf.data() + pos, buf.size() - pos});
}

TxResult newline() noexcept
{
    return write("\r\n");
}

std::optional<char> read() noexcept
{
    if ((USART1->SR & USART_SR_RXNE) == 0) {
        return std::nullopt;
    }
    return static_cast<char>(USART1->DR & 0xFFu);
}

} // namespace console
} // namespace io
