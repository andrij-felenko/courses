/* Той самий поділ праці на восьмибітному ядрі (ATmega328P, avr-libc).
 *
 * AVR цінний тим, що на ньому неатомарність видно неозброєним оком:
 * тридцятидвобітний лічильник імпульсів читається чотирма інструкціями,
 * і переривання, яке вклиниться посередині, дасть число, якого ніколи
 * не існувало. Тому кільце байтів обходиться без критичної секції,
 * а лічильник — не обходиться.
 */
#define F_CPU 16000000UL

#include <avr/interrupt.h>
#include <avr/io.h>
#include <util/atomic.h>

#include "../spsc_ring.h"

#define BAUD 9600UL
#define UBRR_VALUE ((F_CPU / (16UL * BAUD)) - 1UL)

static spsc_ring_buffer_t g_rx_ring;

/* Лічильник імпульсів давача. Ширший за регістр ядра — саме тому й показовий. */
static volatile uint32_t g_pulse_count;

/* Скільки байтів прийшло, поки кільце було повне. */
static volatile uint8_t g_rx_dropped;

/* --------------------------------------------------------------------------
 * ВЕРХНІ ПОЛОВИНИ. Обидві — по кілька інструкцій, без жодного виклику,
 * чия тривалість залежить від зовнішнього світу.
 * ------------------------------------------------------------------------ */
ISR(USART_RX_vect)
{
    /* Читання UDR0 знімає прапорець RXC: окремого квитування немає.
     * Читати треба ОБОВ'ЯЗКОВО, навіть якщо кільце повне, — інакше
     * переривання спрацює знову тієї ж миті й ядро в ньому і залишиться. */
    const uint8_t byte = UDR0;

    if (!ring_buffer_push_isr(&g_rx_ring, byte)) {
        g_rx_dropped++;
    }
}

ISR(INT0_vect)
{
    /* Інкремент 32-бітної змінної тут безпечний: усередині обробника
     * переривання вже заборонені, тож чотири байтові операції ніхто
     * не розірве. Небезпечне — читання цієї змінної ззовні. */
    g_pulse_count++;
}

/* --------------------------------------------------------------------------
 * НИЖНЯ ПОЛОВИНА — головний цикл. Тут дозволено і чекати, і друкувати.
 * ------------------------------------------------------------------------ */
static void uart_put(uint8_t byte)
{
    /* Активне очікування, і воно доречне: ми в контексті main(),
     * переривання дозволені, аварійна лінія обслуговується. */
    while (!(UCSR0A & (1 << UDRE0))) {
    }
    UDR0 = byte;
}

/* Друк без printf: форматований вивід тягне за собою кілька кілобайтів коду
 * і сотні тактів на виклик — а користі тут рівно на десять рядків. */
static void uart_put_u32(uint32_t value)
{
    char digits[10];
    uint8_t n = 0u;

    do {
        digits[n++] = (char)('0' + (value % 10u));
        value /= 10u;
    } while (value != 0u && n < sizeof(digits));

    while (n > 0u) {
        uart_put((uint8_t)digits[--n]);
    }
}

static void uart_put_str(const char *s)
{
    while (*s != '\0') {
        uart_put((uint8_t)*s++);
    }
}

static void hardware_init(void)
{
    /* UART: 9600 8N1, приймач із перериванням, передавач без. */
    UBRR0H = (uint8_t)(UBRR_VALUE >> 8);
    UBRR0L = (uint8_t)(UBRR_VALUE);
    UCSR0B = (1 << RXEN0) | (1 << TXEN0) | (1 << RXCIE0);
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);

    /* INT0 (PD2) за спадним фронтом, із підтяжкою до живлення. */
    PORTD |= (1 << PD2);
    EICRA = (1 << ISC01);
    EIMSK = (1 << INT0);
}

int main(void)
{
    ring_buffer_init(&g_rx_ring);
    hardware_init();
    sei();

    uint32_t reported = 0u;

    for (;;) {
        /* 1. Вичерпуємо кільце. Індекси однобайтові, тож критична секція
         *    не потрібна навіть на восьмибітному ядрі. */
        uint8_t byte;
        while (ring_buffer_pop_main(&g_rx_ring, &byte)) {
            uart_put(byte); /* луна: тут можна, бо це не обробник */
        }

        /* 2. А ось лічильник копіюємо ПІД критичною секцією: інакше
         *    між читанням старших і молодших байтів може влізти INT0. */
        uint32_t pulses;
        ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
        {
            pulses = g_pulse_count;
        }

        if (pulses != reported) {
            reported = pulses;
            uart_put_str("impulses: ");
            uart_put_u32(pulses);
            uart_put('\r');
            uart_put('\n');
        }

        if (g_rx_dropped != 0u) {
            uint8_t dropped;
            ATOMIC_BLOCK(ATOMIC_RESTORESTATE)
            {
                dropped = g_rx_dropped;
                g_rx_dropped = 0u;
            }
            uart_put_str("lost: ");
            uart_put_u32(dropped);
            uart_put('\r');
            uart_put('\n');
        }
    }
}
