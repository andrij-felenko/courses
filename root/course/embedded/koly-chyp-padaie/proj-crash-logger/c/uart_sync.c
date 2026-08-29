#include "uart_sync.h"

#include "stm32f4xx.h"

// Скільки разів опитуємо TXE, перш ніж визнати передавач мертвим. Число підібране
// так, щоб на 168 МГц вийшло помітно більше за час одного символу на 9600 бод.
#define UART_TX_SPIN_LIMIT 2000000u

static bool uart_put(char c)
{
    uint32_t spin = UART_TX_SPIN_LIMIT;
    while (!(USART1->SR & USART_SR_TXE)) {
        if (--spin == 0u) {
            return false; // передавач не звільнився — далі не чекаємо
        }
    }
    USART1->DR = (uint32_t)(uint8_t)c;
    return true;
}

void uart_sync_init(uint32_t pclk2_hz, uint32_t baud)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;

    // PA9 — TX, PA10 — RX, обидві в режимі альтернативної функції AF7.
    GPIOA->MODER &= ~((3u << (9 * 2)) | (3u << (10 * 2)));
    GPIOA->MODER |= (2u << (9 * 2)) | (2u << (10 * 2));
    GPIOA->OSPEEDR |= (3u << (9 * 2)) | (3u << (10 * 2));
    GPIOA->AFR[1] &= ~((0xFu << ((9 - 8) * 4)) | (0xFu << ((10 - 8) * 4)));
    GPIOA->AFR[1] |= (7u << ((9 - 8) * 4)) | (7u << ((10 - 8) * 4));

    // OVER8 = 0: дільник — просто pclk/baud, з округленням до найближчого.
    USART1->BRR = (pclk2_hz + baud / 2u) / baud;
    USART1->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE;
}

bool uart_sync_write_n(const char *data, uint32_t len)
{
    for (uint32_t i = 0; i < len; ++i) {
        if (!uart_put(data[i])) {
            return false;
        }
    }
    return true;
}

bool uart_sync_write(const char *text)
{
    if (text == NULL) {
        return true;
    }
    while (*text != '\0') {
        if (!uart_put(*text++)) {
            return false;
        }
    }
    return true;
}

bool uart_sync_newline(void)
{
    return uart_sync_write("\r\n");
}

bool uart_sync_hex32(uint32_t value)
{
    // Буфер статичний навмисне: обробник може працювати на краю стека, що вже
    // переповнився, і кожен байт локальних змінних там небезпечний.
    static char buf[10];
    static const char digits[] = "0123456789ABCDEF";

    buf[0] = '0';
    buf[1] = 'x';
    for (int i = 0; i < 8; ++i) {
        buf[2 + i] = digits[(value >> ((7 - i) * 4)) & 0xFu];
    }
    return uart_sync_write_n(buf, 10);
}

bool uart_sync_dec(uint32_t value)
{
    static char buf[10];
    int pos = 10;

    if (value == 0u) {
        return uart_sync_write_n("0", 1);
    }
    while (value > 0u && pos > 0) {
        buf[--pos] = (char)('0' + (value % 10u));
        value /= 10u;
    }
    return uart_sync_write_n(&buf[pos], (uint32_t)(10 - pos));
}

bool uart_sync_read(char *out)
{
    if ((USART1->SR & USART_SR_RXNE) == 0u) {
        return false;
    }
    *out = (char)(USART1->DR & 0xFFu);
    return true;
}
