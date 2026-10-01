#ifndef UART_H
#define UART_H

#include <stdint.h>
#include <stdbool.h>

/* Базові адреси регістрів периферії ESP8266 */
#define PERIPHS_UART_BASEADR        0x60000000
#define UART0_BASE                  PERIPHS_UART_BASEADR

/* Регістри UART0 (ESP8266 hardware registers) */
#define UART_FIFO(sys)             (*(volatile uint32_t *)(UART0_BASE + 0x00))
#define UART_INT_RAW(sys)          (*(volatile uint32_t *)(UART0_BASE + 0x04))
#define UART_INT_ST(sys)           (*(volatile uint32_t *)(UART0_BASE + 0x08))
#define UART_INT_ENA(sys)          (*(volatile uint32_t *)(UART0_BASE + 0x0C))
#define UART_INT_CLR(sys)          (*(volatile uint32_t *)(UART0_BASE + 0x10))
#define UART_CLKDIV(sys)           (*(volatile uint32_t *)(UART0_BASE + 0x14))
#define UART_AUTOBAUD(sys)         (*(volatile uint32_t *)(UART0_BASE + 0x18))
#define UART_STATUS(sys)           (*(volatile uint32_t *)(UART0_BASE + 0x1C))
#define UART_CONF0(sys)            (*(volatile uint32_t *)(UART0_BASE + 0x20))
#define UART_CONF1(sys)            (*(volatile uint32_t *)(UART0_BASE + 0x24))

/* Маски статусу FIFO UART */
#define UART_TXFIFO_CNT_S          16
#define UART_TXFIFO_CNT_M          0x00FF0000

/* Розрахунок тактової частоти UART: 80 МГц / 115200 */
#define APB_CLK_FREQ               80000000UL
#define DEFAULT_BAUD_RATE          115200UL

/**
 * Ініціалізація послідовного порту UART0 на задану швидкість
 */
static inline void uart0_init(uint32_t baud_rate) {
    /* Обчислення дільника частоти */
    uint32_t clk_div = APB_CLK_FREQ / baud_rate;
    UART_CLKDIV(0) = clk_div;
    
    /* Конфігурація: 8 біт даних, без парності, 1 стоп-біт (8N1) */
    UART_CONF0(0) = (0x3 << 2) | (0x0 << 0);
}

/**
 * Відправка одного символу через FIFO UART0 з очікуванням вільного місця
 */
static inline void uart_tx_one_char(char c) {
    while (((UART_STATUS(0) >> UART_TXFIFO_CNT_S) & 0xFF) >= 126) {
        /* Чекаємо вивільнення FIFO буфера */
    }
    UART_FIFO(0) = (uint32_t)c;
}

/**
 * Передача нуль-термінованого рядка
 */
static inline void uart_send_string(const char *str) {
    while (*str) {
        if (*str == '\n') {
            uart_tx_one_char('\r');
        }
        uart_tx_one_char(*str++);
    }
}

#endif /* UART_H */
