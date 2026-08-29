#include "uart.h"

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/atomic.h>

#define TX_BUF_SIZE 128u   /* Степінь двійки: маска замість ділення */
#define TX_BUF_MASK (TX_BUF_SIZE - 1u)

static volatile uint8_t  tx_buf[TX_BUF_SIZE];
static volatile uint8_t  tx_head;   /* Куди пише контур */
static volatile uint8_t  tx_tail;   /* Звідки бере переривання */
static volatile uint16_t tx_dropped;

void uart_init(uint32_t baud)
{
    /* Подвійна швидкість (U2X0) дає меншу похибку ділення на 16 МГц:
     * для 115200 це 2.1% замість 3.5%, і приймач на боці ПК не збивається. */
    const uint16_t ubrr = (uint16_t)((F_CPU / (8UL * baud)) - 1UL);

    UBRR0H = (uint8_t)(ubrr >> 8);
    UBRR0L = (uint8_t)ubrr;

    UCSR0A = (1 << U2X0);
    UCSR0B = (1 << TXEN0);
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);   /* 8 біт, без парності, 1 стоп */

    tx_head = tx_tail = 0;
    tx_dropped = 0;
}

ISR(USART_UDRE_vect)
{
    if (tx_head == tx_tail) {
        /* Кільце порожнє — глушимо переривання, інакше воно крутитиметься
         * безперервно й з'їсть увесь запас часу такту. */
        UCSR0B &= (uint8_t)~(1 << UDRIE0);
        return;
    }

    UDR0 = tx_buf[tx_tail];
    tx_tail = (uint8_t)((tx_tail + 1u) & TX_BUF_MASK);
}

static void uart_put(char c)
{
    const uint8_t next = (uint8_t)((tx_head + 1u) & TX_BUF_MASK);

    if (next == tx_tail) {
        tx_dropped++;   /* Кільце повне: губимо байт, але не такт */
        return;
    }

    tx_buf[tx_head] = (uint8_t)c;
    tx_head = next;

    /* Вмикати передавач треба з вимкненими перериваннями: інакше ISR
     * устигне побачити порожнє кільце між записом і дозволом. */
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        UCSR0B |= (1 << UDRIE0);
    }
}

void uart_write(const char *s)
{
    while (*s) {
        uart_put(*s++);
    }
}

void uart_write_i32(int32_t v)
{
    char     digits[11];
    uint8_t  n = 0;
    uint32_t u;

    if (v < 0) {
        uart_put('-');
        u = (uint32_t)(-(v + 1)) + 1u;   /* Обхід INT32_MIN */
    } else {
        u = (uint32_t)v;
    }

    do {
        digits[n++] = (char)('0' + (u % 10u));
        u /= 10u;
    } while (u != 0u);

    while (n != 0u) {
        uart_put(digits[--n]);
    }
}

uint16_t uart_dropped(void)
{
    uint16_t v;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        v = tx_dropped;
    }
    return v;
}
