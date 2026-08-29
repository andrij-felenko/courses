#include "console.h"

#include "mcu.h"

/* PA2 = USART2_TX, альтернативна функція AF7. */
#define PIN_UART_TX 2U
#define AF_USART2   7U

/* APB1 = 42 МГц, ділильник = 42e6 / (16 * 115200) = 22.786:
 * мантиса 22, дробова частина round(0.786 * 16) = 13. */
#define USART2_BRR_115200 ((22U << 4) | 13U)

/* Скільки обертів очікування TXE вважати ознакою мертвого передавача.
 * Один символ на 115200 — близько 87 мкс; на 168 МГц це десятки тисяч
 * тактів, тож із запасом беремо мільйон. */
#define TX_SPIN_LIMIT 1000000U

void console_init(void)
{
    RCC_AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC_APB1ENR |= RCC_APB1ENR_USART2EN;
    mcu_dsb();

    uint32_t moder = GPIOA_MODER;
    moder &= ~(3UL << (PIN_UART_TX * 2U));
    moder |= (2UL << (PIN_UART_TX * 2U)); /* альтернативна функція */
    GPIOA_MODER = moder;

    uint32_t afr = GPIOA_AFRL;
    afr &= ~(0xFUL << (PIN_UART_TX * 4U));
    afr |= ((uint32_t)AF_USART2 << (PIN_UART_TX * 4U));
    GPIOA_AFRL = afr;

    USART2_BRR = USART2_BRR_115200;
    USART2_CR1 = USART_CR1_UE | USART_CR1_TE;
}

void console_write_blocking(const char *data, size_t len)
{
    if (data == NULL) {
        return;
    }
    for (size_t i = 0; i < len; ++i) {
        uint32_t spins = 0;
        while ((USART2_SR & USART_SR_TXE) == 0U) {
            if (++spins > TX_SPIN_LIMIT) {
                /* Передавач не звільняється — кабель від'єднали або
                 * периферія збилася. Мовчки виходимо: діагностика не має
                 * права підвісити систему, яку вона діагностує. */
                return;
            }
        }
        USART2_DR = (uint32_t)(unsigned char)data[i];
    }

    uint32_t spins = 0;
    while ((USART2_SR & USART_SR_TC) == 0U) {
        if (++spins > TX_SPIN_LIMIT) {
            return;
        }
    }
}

void console_puts(const char *s)
{
    if (s == NULL) {
        return;
    }
    size_t len = 0;
    while (s[len] != '\0') {
        ++len;
    }
    console_write_blocking(s, len);
}
