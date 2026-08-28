#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/atomic.h>

// Timer1 — 16-біт. Тік = clk/8 = 16 МГц / 8 = 2 МГц → 0.5 мкс.
// Захоплення знімає лічильник TCNT1 у регістр ICR1 у мить фронту
// на ніжці ICP1 (на Arduino Uno це «пін 8»).
#define TICK_NS 500u

volatile uint16_t g_ticks = 0;   // останній інтервал у тіках
volatile uint8_t  g_ready = 0;   // прапорець «є свіжий вимір»

void capture_init(void) {
    TCCR1A = 0;                    // нормальний режим, без ШІМ
    TCCR1B = (1 << ICNC1)          // вхідний фільтр проти коротких сплесків
           | (1 << ICES1)          // ловити фронт наростання
           | (1 << CS11);          // тік clk/8
    TIMSK1 = (1 << ICIE1);         // дозволити переривання захоплення
    sei();
}

// Фронт на ніжці → залізо вже поклало TCNT1 в ICR1. Обробник лише знімає різницю.
ISR(TIMER1_CAPT_vect) {
    static uint16_t last = 0;
    static uint8_t  have_last = 0;
    uint16_t now = ICR1;                 // читаємо регістр захоплення
    if (have_last) {
        g_ticks = now - last;            // беззнакове: один оберт таймера розсмоктується сам
        g_ready = 1;
    }
    last = now;
    have_last = 1;
}

// Головний цикл: переведення в час і частоту — уже поза обробником.
void poll_measurement(void) {
    if (!g_ready) return;

    uint16_t ticks;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {  // 16-біт читаємо цілим, щоб нове захоплення не розірвало його навпіл
        ticks   = g_ticks;
        g_ready = 0;
    }

    uint32_t period_ns = (uint32_t)ticks * TICK_NS;   // тіки → наносекунди
    if (period_ns == 0) return;                       // захист від ділення на нуль
    uint32_t freq_hz = 1000000000UL / period_ns;      // період → частота
    // ... відправити period_ns / freq_hz далі
}
