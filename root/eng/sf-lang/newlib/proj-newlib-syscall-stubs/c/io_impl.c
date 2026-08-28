/**
 * @file io_impl.c
 * @brief Реалізація потокового введення-виведення для Newlib (C99)
 */
#include "syscall_stubs.h"
#include <errno.h>
#include <sys/reent.h>
#include <sys/stat.h>
#include <string.h>

/* Структура кільцевого буфера FIFO */
typedef struct {
    uint8_t buffer[SYS_UART_TX_RING_BUFFER_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} ring_buffer_tx_t;

typedef struct {
    uint8_t buffer[SYS_UART_RX_RING_BUFFER_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} ring_buffer_rx_t;

static ring_buffer_tx_t g_tx_ring;
static ring_buffer_rx_t g_rx_ring;

/* Симуляція регістрів апаратного UART (наприклад, USART1 у STM32) */
typedef struct {
    volatile uint32_t ISR;  /**< Регістр статусу */
    volatile uint32_t TDR;  /**< Регістр передачі даних */
    volatile uint32_t RDR;  /**< Регістр прийому даних */
    volatile uint32_t CR1;  /**< Регістр керування */
} mock_uart_reg_t;

#define MOCK_UART_BASE ((mock_uart_reg_t *)0x40013800UL)
#define USART_ISR_TXE  (1U << 7)  /**< Прапорець готовності передавача */
#define USART_ISR_RXNE (1U << 5)  /**< Прапорець наявності прийнятого байта */

void syscalls_init(void) {
    memset(&g_tx_ring, 0, sizeof(g_tx_ring));
    memset(&g_rx_ring, 0, sizeof(g_rx_ring));
}

void syscalls_uart_putc_raw(uint8_t c) {
    /* Прямий блокуючий вивід в апаратний регістр без буферизації */
    mock_uart_reg_t *uart = MOCK_UART_BASE;
    while (!(uart->ISR & USART_ISR_TXE)) {
        /* Очікування вивільнення зсувного регістра передавача */
    }
    uart->TDR = c;
}

void syscalls_flush_stdout(void) {
    /* Вичитування всіх байтів із кільцевого буфера у фізичний UART */
    while (g_tx_ring.head != g_tx_ring.tail) {
        uint8_t byte = g_tx_ring.buffer[g_tx_ring.tail];
        g_tx_ring.tail = (g_tx_ring.tail + 1) % SYS_UART_TX_RING_BUFFER_SIZE;
        syscalls_uart_putc_raw(byte);
    }
}

int _write_r(struct _reent *r, int fd, const void *buf, size_t count) {
    const uint8_t *data = (const uint8_t *)buf;

    /* Перевірка дескриптора: дозволено лише stdout (1) та stderr (2) */
    if (fd != 1 && fd != 2) {
        r->_errno = EBADF;
        return -1;
    }

    if (buf == NULL || count == 0) {
        return 0;
    }

    for (size_t i = 0; i < count; ++i) {
        uint8_t c = data[i];

        /* Автоматична підстановка \r перед кожним \n для коректного виводу в термінал */
        if (c == '\n') {
            uint16_t next_head = (g_tx_ring.head + 1) % SYS_UART_TX_RING_BUFFER_SIZE;
            if (next_head != g_tx_ring.tail) {
                g_tx_ring.buffer[g_tx_ring.head] = '\r';
                g_tx_ring.head = next_head;
            } else {
                /* Буфер переповнено: аварійний прямий скид */
                syscalls_uart_putc_raw('\r');
            }
        }

        uint16_t next_head = (g_tx_ring.head + 1) % SYS_UART_TX_RING_BUFFER_SIZE;
        if (next_head != g_tx_ring.tail) {
            g_tx_ring.buffer[g_tx_ring.head] = c;
            g_tx_ring.head = next_head;
        } else {
            /* Буфер переповнено: передаємо безпосередньо у фізичний UART */
            syscalls_uart_putc_raw(c);
        }
    }

    /* Фонове спустошення буфера */
    syscalls_flush_stdout();
    return (int)count;
}

int _write(int fd, const char *buf, int len) {
    return _write_r(_impure_ptr, fd, buf, (size_t)len);
}

int _read_r(struct _reent *r, int fd, void *buf, size_t count) {
    uint8_t *data = (uint8_t *)buf;

    if (fd != 0) { /* Лише stdin */
        r->_errno = EBADF;
        return -1;
    }

    if (buf == NULL || count == 0) {
        return 0;
    }

    size_t bytes_read = 0;
    while (bytes_read < count) {
        /* Якщо в кільцевому буфері є дані — забираємо їх */
        if (g_rx_ring.head != g_rx_ring.tail) {
            uint8_t c = g_rx_ring.buffer[g_rx_ring.tail];
            g_rx_ring.tail = (g_rx_ring.tail + 1) % SYS_UART_RX_RING_BUFFER_SIZE;

            /* Конвертація повернення каретки \r у \n */
            if (c == '\r') {
                c = '\n';
            }

            /* Локальне ехо символу в термінал */
            syscalls_uart_putc_raw(c);

            data[bytes_read++] = c;
            if (c == '\n') {
                break; /* Завершення читання рядка */
            }
        } else {
            /* Якщо буфер порожній — блокуюче очікування з апаратного порту */
            mock_uart_reg_t *uart = MOCK_UART_BASE;
            if (uart->ISR & USART_ISR_RXNE) {
                uint8_t rx_byte = (uint8_t)(uart->RDR & 0xFF);
                uint16_t next_head = (g_rx_ring.head + 1) % SYS_UART_RX_RING_BUFFER_SIZE;
                if (next_head != g_rx_ring.tail) {
                    g_rx_ring.buffer[g_rx_ring.head] = rx_byte;
                    g_rx_ring.head = next_head;
                }
            } else if (bytes_read > 0) {
                /* Частково прочитано дані: повертаємо те, що вже є */
                break;
            }
        }
    }

    return (int)bytes_read;
}

int _read(int fd, char *buf, int len) {
    return _read_r(_impure_ptr, fd, buf, (size_t)len);
}
