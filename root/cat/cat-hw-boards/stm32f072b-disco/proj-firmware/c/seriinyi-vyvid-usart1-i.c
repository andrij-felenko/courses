#include "stm32f0xx.h"

static void uart1_init(void) {
    RCC->AHBENR  |= RCC_AHBENR_GPIOAEN;         // порт A: там PA9/PA10
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;       // USART1 сидить на APB2

    // PA9, PA10 → альтернативна функція AF1 (це USART1 на цих виводах).
    GPIOA->MODER &= ~((3u << (9 * 2)) | (3u << (10 * 2)));
    GPIOA->MODER |=  ((2u << (9 * 2)) | (2u << (10 * 2)));   // 10 = альт. функція
    GPIOA->AFR[1] &= ~((0xFu << ((9 - 8) * 4)) | (0xFu << ((10 - 8) * 4)));
    GPIOA->AFR[1] |=  ((1u   << ((9 - 8) * 4)) | (1u   << ((10 - 8) * 4)));  // AF1

    USART1->BRR = 417;                          // 48 МГц / 115200 ≈ 417
    USART1->CR1 = USART_CR1_TE | USART_CR1_RE | USART_CR1_UE;  // TX, RX, увімкнути
}

static void uart_putc(char c) {
    while (!(USART1->ISR & USART_ISR_TXE)) { }  // чекаємо, поки регістр передачі вільний
    USART1->TDR = (uint8_t)c;
}

static void uart_print(const char *s) {
    while (*s) uart_putc(*s++);
}

// Вивести ціле число зі знаком у десятковому вигляді (без printf — щоб не тягти важку бібліотеку).
static void uart_print_int(int v) {
    char buf[12];
    int i = 0, neg = (v < 0);
    unsigned u = neg ? (unsigned)(-v) : (unsigned)v;
    do { buf[i++] = (char)('0' + u % 10); u /= 10; } while (u);
    if (neg) buf[i++] = '-';
    while (i--) uart_putc(buf[i]);
}
