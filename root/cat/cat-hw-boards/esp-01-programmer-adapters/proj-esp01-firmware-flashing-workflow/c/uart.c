#include "uart.h"
#include <stdio.h>

/**
 * @file uart.c
 * @brief Реалізація низькорівневого драйвера UART для модуля ESP-01.
 * 
 * Здійснює прямий доступ до апаратних регістрів UART0 мікроконтролера ESP8266
 * для налаштування швидкості передачі, баферів FIFO та TX/RX комунікації.
 */

// Базова адреса периферійного модуля UART0 в адресному просторі ESP8266
#define UART0_BASE_ADDR       0x60000000U

// Апаратні регістри UART0
#define UART0_FIFO_REG        (*(volatile uint32_t *)(UART0_BASE_ADDR + 0x00U))
#define UART0_CLKDIV_REG      (*(volatile uint32_t *)(UART0_BASE_ADDR + 0x14U))
#define UART0_STATUS_REG      (*(volatile uint32_t *)(UART0_BASE_ADDR + 0x1CU))
#define UART0_CONF0_REG       (*(volatile uint32_t *)(UART0_BASE_ADDR + 0x20U))

// Бітові прапори конфігураційного регістра CONF0
#define UART_CONF0_TXFIFO_RST (1U << 17)
#define UART_CONF0_RXFIFO_RST (1U << 18)
#define UART_BIT_NUM_8_BITS   (3U << 2) // 8 біт даних у кадрі
#define UART_STOP_BIT_1_BIT   (1U << 4) // 1 стоп-біт у кадрі

// Максимальний розмір апаратного TX FIFO бафера в ESP8266 (128 байт)
#define UART_TXFIFO_MAX_DEPTH 128U

// Частота системної шини APB за замовчуванням (80 МГц)
#define ESP8266_APB_CLK_HZ    80000000U

void uart_init(uint32_t baud_rate) {
    // Якщо передано некоректне значення baud rate, застосовуємо значення за замовчуванням
    if (baud_rate == 0U) {
        baud_rate = UART_DEFAULT_BAUD_RATE;
    }

    // Розрахунок дільника частоти UART: div = APB_CLK / baud_rate
    uint32_t clk_divider = ESP8266_APB_CLK_HZ / baud_rate;
    UART0_CLKDIV_REG = clk_divider;

    // Програмне скидання (очищення) апаратних приймального та передавального баферів FIFO
    UART0_CONF0_REG |= (UART_CONF0_TXFIFO_RST | UART_CONF0_RXFIFO_RST);
    UART0_CONF0_REG &= ~(UART_CONF0_TXFIFO_RST | UART_CONF0_RXFIFO_RST);

    // Налаштування кадру 8N1: 8 біт даних, 1 стоп-біт, без перевірки парності
    uint32_t conf_val = UART0_CONF0_REG;
    conf_val &= ~(0x3U << 2); // Очищення налаштувань бітів даних
    conf_val &= ~(0x3U << 4); // Очищення налаштувань стоп-бітів
    conf_val |= (UART_BIT_NUM_8_BITS | UART_STOP_BIT_1_BIT);
    UART0_CONF0_REG = conf_val;
}

void uart_send_char(char c) {
    // Очікуємо, поки в передавальному бафері TX FIFO з'явиться вільне місце
    // Блок бітів 16..23 регістра UART0_STATUS містить поточну кількість байт у TX FIFO
    while (((UART0_STATUS_REG >> 16) & 0xFFU) >= UART_TXFIFO_MAX_DEPTH) {
        // Активне очікування вивільнення FIFO бафера
    }

    // Відправка байта шляхом запису в регістр даних FIFO
    UART0_FIFO_REG = (uint32_t)((unsigned char)c);
}

void uart_send_string(const char *str) {
    if (str == NULL) {
        return;
    }

    while (*str != '\0') {
        // Нормалізація нового рядка для терміналів серійного порту (додавання \r перед \n)
        if (*str == '\n') {
            uart_send_char('\r');
        }
        uart_send_char(*str);
        str++;
    }
}

void uart_send_diagnostic_status(uint32_t cycle_count, uint32_t uptime_ms) {
    char diagnostic_buf[128];

    // Форматування діагностичного рядка зі збереженням інформації про стан та аптайм
    int formatted_bytes = snprintf(
        diagnostic_buf,
        sizeof(diagnostic_buf),
        "[STATUS] Cycle #%lu | Uptime: %lu ms | ESP-01 UART: OK\n",
        (unsigned long)cycle_count,
        (unsigned long)uptime_ms
    );

    // Відправка сформованого рядка при успішному форматуванні
    if (formatted_bytes > 0) {
        uart_send_string(diagnostic_buf);
    }
}
